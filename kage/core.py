import json
import inspect
from typing import Any, Dict, List, Optional, Callable, Union
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

class Kage:
    """
    Kage Plugin Framework - A JSON schema-based function orchestration system

    This class provides:
    - JSON schema validation for inputs and outputs
    - Function binding and execution with parameter mapping
    - Dependency resolution for function execution order
    - Structured output generation
    """
    def __init__(self,
                 input_schema: Union[Dict, str, Path],
                 output_schema: Optional[Union[Dict, str, Path]] = None):
        """
        Initialize Kage with input data, schema, and optional output schema

        Args:
            input_schema: JSON schema or path to schema file
            output_schema: Optional output schema or path to schema file
        """
        self.input_schema = self._load_json(input_schema)
        self.output_schema = self._load_json(output_schema) if output_schema else {}

        self.functions: Dict[str, FunctionBinding] = {}
        self.execution_results: Dict[str, Any] = {}
        self.output_data: Dict[str, Any] = {}

        # Initialize output structure if schema provided
        if self.output_schema:
            self._initialize_output()

    def _load_json(self, data: Union[Dict, str, Path]) -> Dict:
        """Load JSON data from dict, string, or file path"""
        if isinstance(data, dict):
            return data
        elif isinstance(data, (str, Path)):
            path = Path(data)
            if path.exists():
                with open(path, 'r') as f:
                    return json.load(f)
            else:
                # Try to parse as JSON string
                try:
                    return json.loads(str(data))
                except json.JSONDecodeError:
                    raise KageError(f"Invalid JSON data or file path: {data}")
        else:
            raise KageError(f"Unsupported data type: {type(data)}")

    def _validate_type(self, value: Any, expected_type: str, key_path: str = "") -> bool:
        """Validate a single value against expected type"""
        type_map = {
            DataType.STRING.value: str,
            DataType.INTEGER.value: int,
            DataType.FLOAT.value: (int, float),  # JSON doesn't distinguish int/float
            DataType.BOOLEAN.value: bool,
            DataType.ARRAY.value: list,
            DataType.OBJECT.value: dict,
            DataType.NULL.value: type(None)
        }

        if expected_type not in type_map:
            raise SchemaError(f"Unsupported type '{expected_type}' at {key_path}")

        expected_python_type = type_map[expected_type]
        return isinstance(value, expected_python_type)

    def _validate_input(self, input_data):
        """Validate input data against input schema"""
        self._validate_object(input_data, self.input_schema, "root")

    def _validate_object(self, data: Dict, schema: Dict, path: str = ""):
        """Recursively validate object against schema"""
        if not isinstance(schema, dict):
            raise SchemaError(f"Schema must be an object at {path}")

        # Check required fields
        required = schema.get("required", [])
        for field in required:
            if field not in data:
                raise ValidationError(f"Required field '{field}' missing at {path}")

        # Validate each field
        properties = schema.get("properties", schema)  # Support both formats
        for key, value in data.items():
            if key in properties:
                field_path = f"{path}.{key}" if path != "root" else key
                field_schema = properties[key]

                if isinstance(field_schema, str):
                    # Simple type definition
                    if not self._validate_type(value, field_schema, field_path):
                        raise ValidationError(
                            f"Type mismatch at {field_path}: expected {field_schema}, "
                            f"got {type(value).__name__}"
                        )
                elif isinstance(field_schema, dict):
                    # Complex schema object
                    field_type = field_schema.get("type")
                    if field_type:
                        if not self._validate_type(value, field_type, field_path):
                            raise ValidationError(
                                f"Type mismatch at {field_path}: expected {field_type}, "
                                f"got {type(value).__name__}"
                            )

                    # Recursive validation for nested objects
                    if field_type == DataType.OBJECT.value and "properties" in field_schema:
                        self._validate_object(value, field_schema, field_path)
                    elif field_type == DataType.ARRAY.value and "items" in field_schema:
                        self._validate_array(value, field_schema["items"], field_path)

    def _validate_array(self, data: List, item_schema: Union[str, Dict], path: str):
        """Validate array items against schema"""
        for i, item in enumerate(data):
            item_path = f"{path}[{i}]"
            if isinstance(item_schema, str):
                if not self._validate_type(item, item_schema, item_path):
                    raise ValidationError(
                        f"Array item type mismatch at {item_path}: "
                        f"expected {item_schema}, got {type(item).__name__}"
                    )
            elif isinstance(item_schema, dict):
                item_type = item_schema.get("type")
                if item_type and not self._validate_type(item, item_type, item_path):
                    raise ValidationError(
                        f"Array item type mismatch at {item_path}: "
                        f"expected {item_type}, got {type(item).__name__}"
                    )
                if item_type == DataType.OBJECT.value:
                    self._validate_object(item, item_schema, item_path)

    def _initialize_output(self):
        """Initialize output data structure based on output schema"""

        def init_from_schema(schema: Dict) -> Any:
            if isinstance(schema, str):
                return None  # Will be filled by functions
            elif isinstance(schema, dict):
                schema_type = schema.get("type")
                if schema_type == DataType.OBJECT.value:
                    result = {}
                    properties = schema.get("properties", {})
                    for key, prop_schema in properties.items():
                        result[key] = init_from_schema(prop_schema)
                    return result
                elif schema_type == DataType.ARRAY.value:
                    return []
                else:
                    return None
            return None

        if "properties" in self.output_schema:
            for key, schema in self.output_schema["properties"].items():
                self.output_data[key] = init_from_schema(schema)
        else:
            # Simple schema format
            for key, schema in self.output_schema.items():
                self.output_data[key] = init_from_schema(schema)

    def bind_function(self,
                      func: Callable,
                      input_mapping: Dict[str, str],
                      output_key: Optional[str] = None,
                      dependencies: List[str] = None,
                      name: Optional[str] = None) -> 'Kage':
        """
        Bind a function to be executed with mapped input parameters

        Args:
            func: The function to bind
            input_mapping: Maps function parameter names to input data keys
            output_key: Key in output schema where result should be stored
            dependencies: List of other function names this depends on
            name: Optional name for the function (defaults to func.__name__)

        Returns:
            Self for method chaining
        """
        func_name = name or func.__name__

        # Validate input mapping
        func_signature = inspect.signature(func)
        for param_name in input_mapping.keys():
            if param_name not in func_signature.parameters:
                raise KageError(
                    f"Parameter '{param_name}' not found in function '{func_name}'"
                )



        self.functions[func_name] = FunctionBinding(
            func=func,
            input_mapping=input_mapping,
            output_key=output_key,
            dependencies=dependencies or []
        )

        return self

    def _key_exists_in_data(self, key: str, data: Dict) -> bool:
        """Check if a nested key exists in data (supports dot notation)"""
        keys = key.split('.')
        current = data
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return False
        return True

    def _get_nested_value(self, key: str, data: Dict) -> Any:
        """Get nested value from data using dot notation"""
        keys = key.split('.')
        current = data
        for k in keys:
            current = current[k]
        return current

    def _resolve_execution_order(self) -> List[str]:
        """Resolve function execution order based on dependencies"""
        resolved = []
        remaining = set(self.functions.keys())

        while remaining:
            # Find functions with no unresolved dependencies
            ready = []
            for func_name in remaining:
                binding = self.functions[func_name]
                if all(dep in resolved for dep in binding.dependencies):
                    ready.append(func_name)

            if not ready:
                # Circular dependency or missing dependency
                unresolved_deps = []
                for func_name in remaining:
                    binding = self.functions[func_name]
                    missing_deps = [d for d in binding.dependencies if d not in resolved]
                    if missing_deps:
                        unresolved_deps.append(f"{func_name} -> {missing_deps}")

                raise ExecutionError(f"Circular or missing dependencies: {unresolved_deps}")

            # Add ready functions to resolved list
            for func_name in ready:
                resolved.append(func_name)
                remaining.remove(func_name)

        return resolved

    def execute(self, input_data) -> Dict[str, Any]:
        """
        Execute all bound functions in dependency order

        Returns:
            Dictionary containing the final output data
        """
        self.input_data = input_data

        if not self.functions:
            raise ExecutionError("No functions bound for execution")

        self._validate_input(self.input_data)
        # Validate that mapped input keys exist
        for func_name, func in self.functions.items():
            for input_key in func.input_mapping.values():
                if not self._key_exists_in_data(input_key, self.input_data):
                    raise KageError(f"Input key '{input_key}' not found in input data")
        # Resolve execution order
        execution_order = self._resolve_execution_order()

        # Execute functions in order
        for func_name in execution_order:
            binding = self.functions[func_name]

            try:
                # Prepare function arguments
                kwargs = {}

                for param_name, input_key in binding.input_mapping.items():
                    # Check if input_key refers to another function's output
                    if input_key in self.execution_results:
                        kwargs[param_name] = self.execution_results[input_key]
                    else:
                        kwargs[param_name] = self._get_nested_value(input_key, self.input_data)

                # Execute function
                result = binding.func(**kwargs)

                # Store result
                self.execution_results[func_name] = result

                # Update output data if output key is specified
                if binding.output_key:
                    self._set_nested_value(binding.output_key, result, self.output_data)

            except Exception as e:
                raise ExecutionError(f"Error executing function '{func_name}': {str(e)}") from e

        return self.output_data

    def _set_nested_value(self, key: str, value: Any, data: Dict):
        """Set nested value in data using dot notation"""
        keys = key.split('.')
        current = data

        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]

        current[keys[-1]] = value

    def get_input_value(self, key: str) -> Any:
        """Get value from input data"""
        try:
            return self._get_nested_value(key, self.input_data)
        except ExecutionError as e:
            return e

    def get_execution_result(self, func_name: str) -> Any:
        """Get result from a specific function execution"""
        return self.execution_results.get(func_name)

    def get_output(self) -> Dict[str, Any]:
        """Get the current output data"""
        return self.output_data

    def to_json(self) -> str:
        """Convert output data to JSON string"""
        return json.dumps(self.output_data, indent=2)

    def save_output(self, file_path: Union[str, Path]):
        """Save output data to JSON file"""
        with open(file_path, 'w') as f:
            json.dump(self.output_data, f, indent=2)

    @classmethod
    def from_files(cls,
                   input_file: Union[str, Path],
                   schema_file: Union[str, Path],
                   output_schema_file: Optional[Union[str, Path]] = None) -> 'Kage':
        """
        Create Kage instance from file paths

        Args:
            input_file: Path to input JSON file
            schema_file: Path to input schema JSON file
            output_schema_file: Optional path to output schema JSON file

        Returns:
            Configured Kage instance
        """
        return cls(input_file, schema_file, output_schema_file)
class KageError(Exception):
    """Base exception for Kage framework errors"""
    pass


class ValidationError(KageError):
    """Raised when input validation fails"""
    pass


class ExecutionError(KageError):
    """Raised when function execution fails"""
    pass


class SchemaError(KageError):
    """Raised when schema is invalid"""
    pass


class DataType(Enum):
    """Supported data types for schema validation"""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"
    NULL = "null"


@dataclass
class FunctionBinding:
    """Represents a function bound to specific input parameters"""
    func: Callable
    input_mapping: Dict[str, str]  # Maps function param names to input keys
    output_key: Optional[str] = None  # Key in output schema to store result
    dependencies: List[str] = None  # Other function output keys this depends on

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []

