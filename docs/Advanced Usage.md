## Advanced Usage

### Custom Validation

```python
from kage import core


class CustomKage(Kage):
    def _validate_input(self):
        # Call parent validation first
        super()._validate_input()

        # Add custom validation
        if "email" in self.input_data:
            email = self.input_data["email"]
            if not email.endswith("@company.com"):
                raise ValidationError("Email must be from company domain")
```

### Dynamic Function Loading

```python
import importlib
from pathlib import Path

def load_plugin_functions(plugin_dir):
    """Dynamically load functions from plugin directory"""
    
    plugin_path = Path(plugin_dir)
    functions = {}
    
    for py_file in plugin_path.glob("*.py"):
        if py_file.name.startswith("__"):
            continue
            
        # Import module
        spec = importlib.util.spec_from_file_location(
            py_file.stem, py_file
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Extract functions
        for name in dir(module):
            obj = getattr(module, name)
            if callable(obj) and not name.startswith("_"):
                functions[name] = obj
    
    return functions

# Usage
plugin_functions = load_plugin_functions("./plugins/math_ops/")
kage = Kage(input_data, schema)

for name, func in plugin_functions.items():
    # Auto-bind based on function signature
    sig = inspect.signature(func)
    mapping = {param: param for param in sig.parameters}
    kage.bind_function(func, mapping, output_key=name)
```

### Middleware Support

```python
class MiddlewareKage(Kage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.middlewares = []
    
    def add_middleware(self, middleware_func):
        """Add middleware function"""
        self.middlewares.append(middleware_func)
        return self
    
    def execute(self):
        # Pre-execution middleware
        for middleware in self.middlewares:
            if hasattr(middleware, 'before_execute'):
                middleware.before_execute(self)
        
        # Execute normally
        result = super().execute()
        
        # Post-execution middleware
        for middleware in reversed(self.middlewares):
            if hasattr(middleware, 'after_execute'):
                result = middleware.after_execute(self, result)
        
        return result

# Example middleware
class LoggingMiddleware:
    def before_execute(self, kage):
        print(f"Starting execution with {len(kage.functions)} functions")
    
    def after_execute(self, kage, result):
        print(f"Execution completed. Output keys: {list(result.keys())}")
        return result

# Usage
kage = MiddlewareKage(input_data, schema)
kage.add_middleware(LoggingMiddleware())
```

### Async Support

```python
import asyncio
from typing import Awaitable

class AsyncKage(Kage):
    async def execute_async(self):
        """Execute functions asynchronously where possible"""
        
        execution_order = self._resolve_execution_order()
        completed = set()
        
        for func_name in execution_order:
            binding = self.functions[func_name]
            
            # Check if all dependencies are completed
            if all(dep in completed for dep in binding.dependencies):
                # Prepare arguments
                kwargs = {}
                for param_name, input_key in binding.input_mapping.items():
                    if input_key in self.execution_results:
                        kwargs[param_name] = self.execution_results[input_key]
                    else:
                        kwargs[param_name] = self._get_nested_value(input_key, self.input_data)
                
                # Execute function (async or sync)
                if asyncio.iscoroutinefunction(binding.func):
                    result = await binding.func(**kwargs)
                else:
                    result = binding.func(**kwargs)
                
                # Store result
                self.execution_results[func_name] = result
                completed.add(func_name)
                
                # Update output
                if binding.output_key:
                    self._set_nested_value(binding.output_key, result, self.output_data)
        
        return self.output_data

# Example async usage
async def async_api_call(url):
    # Simulate API call
    await asyncio.sleep(1)
    return {"status": "success", "data": f"Response from {url}"}

async def process_responses(api_response, local_data):
    # Process both async and sync data
    return {
        "combined": api_response["data"] + " - " + local_data,
        "processed_at": "2024-01-01"
    }

# Usage
async def main():
    input_data = {
        "api_url": "https://api.example.com/data",
        "local_data": "Local information"
    }
    
    kage = AsyncKage(input_data, {})
    kage.bind_function(
        async_api_call,
        {"url": "api_url"},
        output_key="api_response"
    ).bind_function(
        process_responses,
        {"api_response": "async_api_call", "local_data": "local_data"},
        output_key="final_result",
        dependencies=["async_api_call"]
    )
    
    result = await kage.execute_async()
    print(result)

# Run async example
# asyncio.run(main())
```

### Parallel Execution

```python
import concurrent.futures
from typing import List, Dict, Any

class ParallelKage(Kage):
    def __init__(self, *args, max_workers=4, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_workers = max_workers
    
    def execute_parallel(self):
        """Execute independent functions in parallel"""
        
        execution_order = self._resolve_execution_order()
        completed = set()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            while len(completed) < len(self.functions):
                # Find functions ready to execute
                ready_functions = []
                for func_name in execution_order:
                    if (func_name not in completed and 
                        all(dep in completed for dep in self.functions[func_name].dependencies)):
                        ready_functions.append(func_name)
                
                if not ready_functions:
                    break
                
                # Submit functions for parallel execution
                future_to_func = {}
                for func_name in ready_functions:
                    binding = self.functions[func_name]
                    
                    # Prepare arguments
                    kwargs = {}
                    for param_name, input_key in binding.input_mapping.items():
                        if input_key in self.execution_results:
                            kwargs[param_name] = self.execution_results[input_key]
                        else:
                            kwargs[param_name] = self._get_nested_value(input_key, self.input_data)
                    
                    # Submit to executor
                    future = executor.submit(binding.func, **kwargs)
                    future_to_func[future] = func_name
                
                # Collect results
                for future in concurrent.futures.as_completed(future_to_func):
                    func_name = future_to_func[future]
                    binding = self.functions[func_name]
                    
                    try:
                        result = future.result()
                        self.execution_results[func_name] = result
                        completed.add(func_name)
                        
                        if binding.output_key:
                            self._set_nested_value(binding.output_key, result, self.output_data)
                    
                    except Exception as e:
                        raise ExecutionError(f"Parallel execution failed for '{func_name}': {e}")
        
        return self.output_data
```

### Configuration Management

```python
from typing import Optional
import os

class ConfigurableKage(Kage):
    def __init__(self, *args, config_file: Optional[str] = None, **kwargs):
        # Load configuration
        self.config = self._load_config(config_file)
        
        # Apply configuration to initialization
        if "validation" in self.config:
            self.strict_validation = self.config["validation"].get("strict", True)
            self.allow_extra_fields = self.config["validation"].get("allow_extra", False)
        
        super().__init__(*args, **kwargs)
    
    def _load_config(self, config_file: Optional[str]) -> Dict[str, Any]:
        """Load configuration from file or environment"""
        config = {
            "validation": {
                "strict": True,
                "allow_extra": False
            },
            "execution": {
                "parallel": False,
                "max_workers": 4,
                "timeout": 30
            },
            "output": {
                "format": "json",
                "pretty_print": True
            }
        }
        
        # Override with file config
        if config_file and os.path.exists(config_file):
            with open(config_file) as f:
                file_config = json.load(f)
                self._deep_update(config, file_config)
        
        # Override with environment variables
        env_config = self._load_env_config()
        self._deep_update(config, env_config)
        
        return config
    
    def _load_env_config(self) -> Dict[str, Any]:
        """Load configuration from environment variables"""
        config = {}
        
        # KAGE_VALIDATION_STRICT=true
        if os.getenv("KAGE_VALIDATION_STRICT"):
            config.setdefault("validation", {})["strict"] = (
                os.getenv("KAGE_VALIDATION_STRICT").lower() == "true"
            )
        
        # KAGE_EXECUTION_PARALLEL=true
        if os.getenv("KAGE_EXECUTION_PARALLEL"):
            config.setdefault("execution", {})["parallel"] = (
                os.getenv("KAGE_EXECUTION_PARALLEL").lower() == "true"
            )
        
        return config
    
    def _deep_update(self, base_dict: Dict, update_dict: Dict):
        """Deep update dictionary"""
        for key, value in update_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                self._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value
    
    def execute(self):
        """Execute with configuration-based behavior"""
        if self.config["execution"].get("parallel", False):
            return self._execute_parallel()
        else:
            return super().execute()
```

### Plugin Discovery and Auto-Loading

```python
import pkgutil
import importlib
from abc import ABC, abstractmethod

class KagePlugin(ABC):
    """Base class for Kage plugins"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        pass
    
    @property
    @abstractmethod
    def input_schema(self) -> Dict[str, Any]:
        pass
    
    @property
    def output_schema(self) -> Optional[Dict[str, Any]]:
        return None
    
    @abstractmethod
    def configure_kage(self, kage: Kage) -> Kage:
        """Configure the Kage instance with plugin functions"""
        pass

class PluginManager:
    def __init__(self):
        self.plugins: Dict[str, KagePlugin] = {}
    
    def discover_plugins(self, package_name: str = "plugins"):
        """Discover and load plugins from package"""
        try:
            package = importlib.import_module(package_name)
        except ImportError:
            return
        
        for finder, name, ispkg in pkgutil.iter_modules(package.__path__, package.__name__ + "."):
            try:
                module = importlib.import_module(name)
                
                # Look for plugin classes
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and 
                        issubclass(attr, KagePlugin) and 
                        attr != KagePlugin):
                        
                        plugin_instance = attr()
                        self.plugins[plugin_instance.name] = plugin_instance
                        
            except Exception as e:
                print(f"Failed to load plugin {name}: {e}")
    
    def get_plugin(self, name: str) -> Optional[KagePlugin]:
        return self.plugins.get(name)
    
    def list_plugins(self) -> List[str]:
        return list(self.plugins.keys())
    
    def execute_plugin(self, plugin_name: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific plugin"""
        plugin = self.get_plugin(plugin_name)
        if not plugin:
            raise ValueError(f"Plugin '{plugin_name}' not found")
        
        # Create Kage instance
        kage = Kage(input_data, plugin.input_schema, plugin.output_schema)
        
        # Configure with plugin
        configured_kage = plugin.configure_kage(kage)
        
        # Execute
        return configured_kage.execute()

# Example plugin implementation
class UserProcessingPlugin(KagePlugin):
    @property
    def name(self) -> str:
        return "user_processing"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "required": ["users"],
            "properties": {
                "users": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": "string",
                            "email": "string",
                            "age": "integer"
                        }
                    }
                }
            }
        }
    
    @property
    def output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "processed_users": {
                    "type": "array",
                    "items": "object"
                },
                "statistics": "object"
            }
        }
    
    def validate_email(self, email: str) -> bool:
        return "@" in email and "." in email
    
    def categorize_age(self, age: int) -> str:
        if age < 18:
            return "minor"
        elif age < 65:
            return "adult"
        else:
            return "senior"
    
    def process_users(self, users: List[Dict]) -> List[Dict]:
        processed = []
        for user in users:
            processed_user = {
                **user,
                "email_valid": self.validate_email(user["email"]),
                "age_category": self.categorize_age(user["age"])
            }
            processed.append(processed_user)
        return processed
    
    def calculate_statistics(self, processed_users: List[Dict]) -> Dict[str, Any]:
        total = len(processed_users)
        valid_emails = sum(1 for u in processed_users if u["email_valid"])
        avg_age = sum(u["age"] for u in processed_users) / total if total > 0 else 0
        
        return {
            "total_users": total,
            "valid_email_percentage": (valid_emails / total * 100) if total > 0 else 0,
            "average_age": round(avg_age, 2)
        }
    
    def configure_kage(self, kage: Kage) -> Kage:
        return (kage
                .bind_function(
                    self.process_users,
                    {"users": "users"},
                    output_key="processed_users"
                )
                .bind_function(
                    self.calculate_statistics,
                    {"processed_users": "process_users"},
                    output_key="statistics",
                    dependencies=["process_users"]
                ))

# Usage example
def main():
    # Initialize plugin manager
    manager = PluginManager()
    manager.discover_plugins()
    
    print("Available plugins:", manager.list_plugins())
    
    # Execute plugin
    input_data = {
        "users": [
            {"name": "Alice", "email": "alice@example.com", "age": 28},
            {"name": "Bob", "email": "bob@test.com", "age": 35},
            {"name": "Charlie", "email": "invalid-email", "age": 17}
        ]
    }
    
    result = manager.execute_plugin("user_processing", input_data)
    print("Plugin result:", json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
```

