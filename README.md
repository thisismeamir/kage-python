# Kage Framework Documentation

## Table of Contents
1. [Overview](#overview)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Core Concepts](#core-concepts)
5. [API Reference](#api-reference)
6. [Usage Examples](#usage-examples)
7. [Integration Guide](#integration-guide)
8. [Error Handling](#error-handling)
9. [Best Practices](#best-practices)
10. [Advanced Usage](#advanced-usage)

## Overview

Kage is a Python framework for building JSON schema-validated plugins with function orchestration capabilities. It enables you to:

- Validate input data against JSON schemas
- Bind functions to input parameters with automatic mapping
- Execute functions in dependency order
- Generate structured JSON output
- Build reusable plugins for server applications

**Key Benefits:**
- Type-safe plugin development
- Automatic dependency resolution
- Standardized input/output handling
- Easy integration with existing projects
- Comprehensive error reporting

## Installation

### From Source
```bash
# Clone or copy the kage.py file to your project
cp kage.py your_project/
```

### As a Package
```python
# Import the framework
from kage import Kage, KageError, ValidationError, ExecutionError
```

### Dependencies
- Python 3.7+
- Standard library only (no external dependencies)

## Quick Start

### 1. Define Your Data and Schema

```python
from kage import Kage

# Input data
input_data = {
    "user": {
        "name": "Alice",
        "age": 28,
        "email": "alice@example.com"
    },
    "settings": {
        "theme": "dark",
        "language": "en"
    }
}

# Input schema
input_schema = {
    "type": "object",
    "required": ["user"],
    "properties": {
        "user": {
            "type": "object",
            "properties": {
                "name": "string",
                "age": "integer",
                "email": "string"
            }
        },
        "settings": {
            "type": "object",
            "properties": {
                "theme": "string",
                "language": "string"
            }
        }
    }
}

# Output schema (optional)
output_schema = {
    "type": "object",
    "properties": {
        "greeting": "string",
        "user_summary": "string"
    }
}
```

### 2. Create Plugin Functions

```python
def create_greeting(name: str, theme: str) -> str:
    if theme == "dark":
        return f"🌙 Good evening, {name}!"
    return f"☀️ Hello, {name}!"

def summarize_user(name: str, age: int, email: str) -> str:
    return f"{name} is {age} years old and can be reached at {email}"
```

### 3. Configure and Execute

```python
# Initialize Kage
kage = Kage(input_data, input_schema, output_schema)

# Bind functions
kage.bind_function(
    create_greeting,
    {"name": "user.name", "theme": "settings.theme"},
    output_key="greeting"
).bind_function(
    summarize_user,
    {"name": "user.name", "age": "user.age", "email": "user.email"},
    output_key="user_summary"
)

# Execute and get results
result = kage.execute()
print(kage.to_json())
```

**Output:**
```json
{
  "greeting": "🌙 Good evening, Alice!",
  "user_summary": "Alice is 28 years old and can be reached at alice@example.com"
}
```

## Core Concepts

### Schema Validation

Kage validates input data against JSON schemas before execution. Supported types:

- `"string"` - Text values
- `"integer"` - Whole numbers
- `"float"` - Decimal numbers (also accepts integers)
- `"boolean"` - True/false values
- `"array"` - Lists of values
- `"object"` - Nested dictionaries
- `"null"` - None values

### Function Binding

Functions are bound to the Kage instance with:
- **Input mapping**: Maps function parameters to input data keys
- **Output key**: Where to store the function result
- **Dependencies**: Other functions this function depends on

### Execution Order

Kage automatically resolves function dependencies and executes them in the correct order. Functions can depend on:
- Input data values
- Results from other functions

### Nested Data Access

Use dot notation to access nested data:
- `"user.name"` → `input_data["user"]["name"]`
- `"settings.theme"` → `input_data["settings"]["theme"]`

## API Reference

### Kage Class

#### Constructor

```python
Kage(input_data, input_schema, output_schema=None)
```

**Parameters:**
- `input_data` (dict|str|Path): Input data or path to JSON file
- `input_schema` (dict|str|Path): Schema for validation or path to schema file
- `output_schema` (dict|str|Path, optional): Output schema or path to schema file

**Raises:**
- `ValidationError`: When input doesn't match schema
- `SchemaError`: When schema is invalid
- `KageError`: For other initialization errors

#### Methods

##### bind_function()
```python
bind_function(func, input_mapping, output_key=None, dependencies=None, name=None)
```

Bind a function for execution.

**Parameters:**
- `func` (callable): Function to bind
- `input_mapping` (dict): Maps function params to input keys
- `output_key` (str, optional): Output key for storing result
- `dependencies` (list, optional): List of function names this depends on
- `name` (str, optional): Custom name for the function

**Returns:** `Kage` instance (for method chaining)

##### execute()
```python
execute() -> dict
```

Execute all bound functions in dependency order.

**Returns:** Dictionary with output data
**Raises:** `ExecutionError` if execution fails

##### get_input_value()
```python
get_input_value(key: str) -> Any
```

Get value from input data using dot notation.

##### get_execution_result()
```python
get_execution_result(func_name: str) -> Any
```

Get result from a specific function execution.

##### get_output()
```python
get_output() -> dict
```

Get current output data.

##### to_json()
```python
to_json() -> str
```

Convert output to JSON string.

##### save_output()
```python
save_output(file_path)
```

Save output to JSON file.

#### Class Methods

##### from_files()
```python
Kage.from_files(input_file, schema_file, output_schema_file=None)
```

Create Kage instance from file paths.

### Exception Classes

- `KageError`: Base exception
- `ValidationError`: Input validation failures
- `ExecutionError`: Function execution failures  
- `SchemaError`: Schema validation failures

## Usage Examples

### Example 1: Simple Data Processing

```python
from kage import Kage

# Process user orders
input_data = {
    "order": {
        "items": [
            {"name": "Laptop", "price": 999.99, "quantity": 1},
            {"name": "Mouse", "price": 29.99, "quantity": 2}
        ],
        "discount_code": "SAVE10"
    },
    "user": {
        "membership": "premium"
    }
}

input_schema = {
    "type": "object",
    "properties": {
        "order": {
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": "string",
                            "price": "float",
                            "quantity": "integer"
                        }
                    }
                },
                "discount_code": "string"
            }
        },
        "user": {
            "type": "object",
            "properties": {
                "membership": "string"
            }
        }
    }
}

def calculate_subtotal(items):
    return sum(item["price"] * item["quantity"] for item in items)

def apply_discount(subtotal, discount_code, membership):
    discount = 0.1 if discount_code == "SAVE10" else 0
    if membership == "premium":
        discount += 0.05
    return subtotal * (1 - discount)

kage = Kage(input_data, input_schema)
kage.bind_function(
    calculate_subtotal,
    {"items": "order.items"},
    output_key="subtotal"
).bind_function(
    apply_discount,
    {
        "subtotal": "calculate_subtotal",  # Depend on previous function
        "discount_code": "order.discount_code",
        "membership": "user.membership"
    },
    output_key="total",
    dependencies=["calculate_subtotal"]
)

result = kage.execute()
print(f"Subtotal: ${result['subtotal']:.2f}")
print(f"Total: ${result['total']:.2f}")
```

### Example 2: File-Based Configuration

```python
# config/input.json
{
    "database": {
        "host": "localhost",
        "port": 5432,
        "name": "myapp"
    },
    "features": {
        "caching": true,
        "logging": "info"
    }
}

# config/schema.json
{
    "type": "object",
    "required": ["database"],
    "properties": {
        "database": {
            "type": "object",
            "properties": {
                "host": "string",
                "port": "integer",
                "name": "string"
            }
        },
        "features": {
            "type": "object",
            "properties": {
                "caching": "boolean",
                "logging": "string"
            }
        }
    }
}
```

```python
# main.py
from kage import Kage

def create_db_url(host, port, name):
    return f"postgresql://{host}:{port}/{name}"

def setup_logging(logging_level, caching_enabled):
    config = {"level": logging_level}
    if caching_enabled:
        config["cache_logs"] = True
    return config

# Load from files
kage = Kage.from_files("config/input.json", "config/schema.json")

kage.bind_function(
    create_db_url,
    {"host": "database.host", "port": "database.port", "name": "database.name"},
    output_key="database_url"
).bind_function(
    setup_logging,
    {"logging_level": "features.logging", "caching_enabled": "features.caching"},
    output_key="logging_config"
)

config = kage.execute()
print("Generated configuration:")
print(kage.to_json())
```

### Example 3: Complex Dependencies

```python
from kage import Kage

input_data = {
    "text": "Hello World! This is a test.",
    "options": {
        "include_stats": True,
        "format": "detailed"
    }
}

def tokenize_text(text):
    return text.split()

def count_words(tokens):
    return len(tokens)

def count_characters(text):
    return len(text)

def calculate_avg_word_length(tokens):
    return sum(len(token) for token in tokens) / len(tokens) if tokens else 0

def create_report(word_count, char_count, avg_length, format_type):
    if format_type == "detailed":
        return {
            "words": word_count,
            "characters": char_count,
            "average_word_length": round(avg_length, 2),
            "readability": "simple" if avg_length < 5 else "complex"
        }
    return {"words": word_count, "characters": char_count}

kage = Kage(input_data, {})

# Build processing pipeline
kage.bind_function(
    tokenize_text,
    {"text": "text"},
    name="tokenize"
).bind_function(
    count_words,
    {"tokens": "tokenize"},
    output_key="word_count",
    dependencies=["tokenize"]
).bind_function(
    count_characters,
    {"text": "text"},
    output_key="char_count"
).bind_function(
    calculate_avg_word_length,
    {"tokens": "tokenize"},
    name="avg_length",
    dependencies=["tokenize"]
).bind_function(
    create_report,
    {
        "word_count": "count_words",
        "char_count": "count_characters", 
        "avg_length": "avg_length",
        "format_type": "options.format"
    },
    output_key="report",
    dependencies=["count_words", "count_characters", "avg_length"]
)

result = kage.execute()
print("Text Analysis Report:")
print(kage.to_json())
```

## Integration Guide

### Integration with Flask Applications

```python
from flask import Flask, request, jsonify
from kage import Kage, ValidationError, ExecutionError

app = Flask(__name__)

# Plugin registry
plugins = {}

def register_plugin(name, plugin_func):
    """Register a plugin function"""
    plugins[name] = plugin_func

def email_processor_plugin():
    """Example email processing plugin"""
    
    schema = {
        "type": "object",
        "required": ["email", "template"],
        "properties": {
            "email": {
                "type": "object",
                "properties": {
                    "to": "string",
                    "subject": "string"
                }
            },
            "template": "string",
            "variables": "object"
        }
    }
    
    def validate_email(to, subject):
        return "@" in to and len(subject) > 0
    
    def render_template(template, variables):
        # Simple template rendering
        result = template
        if variables:
            for key, value in variables.items():
                result = result.replace(f"{{{key}}}", str(value))
        return result
    
    def create_email_config(template, input_data):
        kage = Kage(input_data, schema)
        
        kage.bind_function(
            validate_email,
            {"to": "email.to", "subject": "email.subject"},
            output_key="is_valid"
        ).bind_function(
            render_template,
            {"template": "template", "variables": "variables"},
            output_key="rendered_content"
        )
        
        return kage.execute()
    
    return create_email_config

# Register plugins
register_plugin("email_processor", email_processor_plugin())

@app.route('/execute_plugin/<plugin_name>', methods=['POST'])
def execute_plugin(plugin_name):
    if plugin_name not in plugins:
        return jsonify({"error": "Plugin not found"}), 404
    
    try:
        input_data = request.get_json()
        plugin = plugins[plugin_name]
        result = plugin(input_data)
        return jsonify(result)
    
    except ValidationError as e:
        return jsonify({"error": "Validation failed", "details": str(e)}), 400
    except ExecutionError as e:
        return jsonify({"error": "Execution failed", "details": str(e)}), 500
    except Exception as e:
        return jsonify({"error": "Internal error", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
```

### Integration with FastAPI

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from kage import Kage, ValidationError, ExecutionError

app = FastAPI(title="Kage Plugin Server")

class PluginRequest(BaseModel):
    input_data: Dict[str, Any]
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any] = None

class PluginModule:
    def __init__(self, name: str):
        self.name = name
        self.functions = {}
    
    def add_function(self, func, input_mapping, output_key=None, dependencies=None):
        self.functions[func.__name__] = {
            "func": func,
            "input_mapping": input_mapping,
            "output_key": output_key,
            "dependencies": dependencies
        }
        return self
    
    def execute(self, input_data, input_schema, output_schema=None):
        kage = Kage(input_data, input_schema, output_schema)
        
        for name, config in self.functions.items():
            kage.bind_function(
                config["func"],
                config["input_mapping"],
                config["output_key"],
                config["dependencies"],
                name
            )
        
        return kage.execute()

# Example plugin module
user_plugin = PluginModule("user_processor")

def validate_user_age(age):
    return age >= 18

def format_user_name(first_name, last_name):
    return f"{first_name.title()} {last_name.title()}"

def create_user_profile(formatted_name, age, is_adult):
    return {
        "name": formatted_name,
        "age": age,
        "status": "adult" if is_adult else "minor",
        "can_vote": is_adult
    }

user_plugin.add_function(
    validate_user_age,
    {"age": "user.age"},
    output_key="is_adult"
).add_function(
    format_user_name,
    {"first_name": "user.first_name", "last_name": "user.last_name"},
    output_key="formatted_name"
).add_function(
    create_user_profile,
    {
        "formatted_name": "format_user_name",
        "age": "user.age",
        "is_adult": "validate_user_age"
    },
    output_key="profile",
    dependencies=["format_user_name", "validate_user_age"]
)

@app.post("/plugins/user_processor")
async def execute_user_plugin(request: PluginRequest):
    try:
        result = user_plugin.execute(
            request.input_data,
            request.input_schema,
            request.output_schema
        )
        return {"success": True, "data": result}
    
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"Validation error: {e}")
    except ExecutionError as e:
        raise HTTPException(status_code=500, detail=f"Execution error: {e}")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "framework": "Kage"}
```

### Plugin Directory Structure

```
your_project/
├── plugins/
│   ├── __init__.py
│   ├── user_management/
│   │   ├── __init__.py
│   │   ├── plugin.py
│   │   ├── schema.json
│   │   └── config.json
│   ├── data_processing/
│   │   ├── __init__.py
│   │   ├── plugin.py
│   │   └── schema.json
│   └── notifications/
│       ├── __init__.py
│       ├── plugin.py
│       └── schema.json
├── kage.py
└── main.py
```

Example plugin structure:

```python
# plugins/user_management/plugin.py
from kage import Kage
import json
from pathlib import Path

class UserManagementPlugin:
    def __init__(self):
        plugin_dir = Path(__file__).parent
        with open(plugin_dir / "schema.json") as f:
            self.schema = json.load(f)
    
    def hash_password(self, password):
        # Simplified hashing
        return f"hashed_{password}"
    
    def validate_email(self, email):
        return "@" in email and "." in email
    
    def create_user(self, username, email, password):
        return {
            "username": username,
            "email": email,
            "password_hash": self.hash_password(password),
            "email_valid": self.validate_email(email),
            "created_at": "2024-01-01T00:00:00Z"
        }
    
    def process(self, input_data):
        kage = Kage(input_data, self.schema)
        
        kage.bind_function(
            self.hash_password,
            {"password": "user.password"},
            name="hash_password"
        ).bind_function(
            self.validate_email,
            {"email": "user.email"},
            name="validate_email"
        ).bind_function(
            self.create_user,
            {
                "username": "user.username",
                "email": "user.email", 
                "password": "user.password"
            },
            output_key="created_user"
        )
        
        return kage.execute()

# plugins/user_management/schema.json
{
    "type": "object",
    "required": ["user"],
    "properties": {
        "user": {
            "type": "object",
            "required": ["username", "email", "password"],
            "properties": {
                "username": "string",
                "email": "string",
                "password": "string"
            }
        }
    }
}
```

## Error Handling

### Exception Types

```python
from kage import ValidationError, ExecutionError, SchemaError, KageError

try:
    kage = Kage(input_data, input_schema)
    result = kage.execute()
    
except ValidationError as e:
    print(f"Input validation failed: {e}")
    # Handle invalid input data
    
except SchemaError as e:
    print(f"Schema is invalid: {e}")
    # Handle schema errors
    
except ExecutionError as e:
    print(f"Function execution failed: {e}")
    # Handle runtime errors
    
except KageError as e:
    print(f"General Kage error: {e}")
    # Handle other framework errors
```

### Validation Error Details

```python
# Example of detailed validation error
input_data = {
    "user": {
        "name": "John",
        "age": "thirty"  # Should be integer
    }
}

schema = {
    "type": "object",
    "properties": {
        "user": {
            "type": "object",
            "properties": {
                "name": "string",
                "age": "integer"
            }
        }
    }
}

try:
    kage = Kage(input_data, schema)
except ValidationError as e:
    print(e)  # "Type mismatch at user.age: expected integer, got str"
```

### Graceful Error Recovery

```python
def safe_plugin_execution(input_data, schema, functions):
    """Execute plugin with comprehensive error handling"""
    
    try:
        kage = Kage(input_data, schema)
        
        # Bind functions
        for func_config in functions:
            kage.bind_function(**func_config)
        
        # Execute
        result = kage.execute()
        
        return {
            "success": True,
            "data": result,
            "errors": []
        }
        
    except ValidationError as e:
        return {
            "success": False,
            "data": None,
            "errors": [{"type": "validation", "message": str(e)}]
        }
        
    except ExecutionError as e:
        return {
            "success": False,
            "data": kage.get_output() if 'kage' in locals() else None,
            "errors": [{"type": "execution", "message": str(e)}]
        }
        
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "errors": [{"type": "unexpected", "message": str(e)}]
        }
```

## Best Practices

### 1. Schema Design

**✅ Good:**
```python
schema = {
    "type": "object",
    "required": ["user", "action"],
    "properties": {
        "user": {
            "type": "object",
            "required": ["id", "email"],
            "properties": {
                "id": "integer",
                "email": "string",
                "name": "string"  # Optional field
            }
        },
        "action": "string"
    }
}
```

**❌ Avoid:**
```python
# Too loose - no validation
schema = {}

# Too strict - hard to extend
schema = {
    "type": "object",
    "required": ["user", "action", "timestamp", "metadata"],
    "properties": {
        "user": {"type": "object"},  # No inner validation
        "action": "string"
    }
}
```

### 2. Function Design

**✅ Good:**
```python
def process_order(items, tax_rate, discount=0):
    """Pure function with clear parameters"""
    subtotal = sum(item["price"] * item["quantity"] for item in items)
    taxed_amount = subtotal * (1 + tax_rate)
    return taxed_amount * (1 - discount)

# Clear binding
kage.bind_function(
    process_order,
    {
        "items": "order.items",
        "tax_rate": "settings.tax_rate",
        "discount": "user.discount_rate"
    },
    output_key="total_amount"
)
```

**❌ Avoid:**
```python
def process_order(data):
    """Function that does too much"""
    # Accessing nested data inside function
    items = data["order"]["items"]
    # Complex logic mixed with data access
    # Side effects like logging, database calls
    return complex_calculation(items)
```

### 3. Dependency Management

**✅ Good:**
```python
# Clear dependency chain
kage.bind_function(step1, {...}, name="step1")
kage.bind_function(step2, {...}, dependencies=["step1"])
kage.bind_function(step3, {...}, dependencies=["step1", "step2"])
```

**❌ Avoid:**
```python
# Circular dependencies
kage.bind_function(func_a, {...}, dependencies=["func_b"])
kage.bind_function(func_b, {...}, dependencies=["func_a"])
```

### 4. Error Handling

**✅ Good:**
```python
def safe_calculation(value):
    if value < 0:
        raise ValueError("Value must be non-negative")
    return math.sqrt(value)

try:
    result = kage.execute()
except ExecutionError as e:
    logger.error(f"Calculation failed: {e}")
    # Provide fallback or alternative
```

### 5. Testing

```python
import unittest
from kage import Kage, ValidationError

class TestMyPlugin(unittest.TestCase):
    def setUp(self):
        self.input_data = {"value": 42}
        self.schema = {
            "type": "object",
            "properties": {"value": "integer"}
        }
    
    def test_valid_input(self):
        kage = Kage(self.input_data, self.schema)
        kage.bind_function(lambda x: x * 2, {"x": "value"}, "result")
        result = kage.execute()
        self.assertEqual(result["result"], 84)
    
    def test_invalid_input(self):
        invalid_data = {"value": "not a number"}
        with self.assertRaises(ValidationError):
            Kage(invalid_data, self.schema)
```

## Advanced Usage

### Custom Validation

```python
from kage import Kage

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

## Performance Optimization

### Memory-Optimized Execution

```python
import gc
from typing import Iterator

class StreamingKage(Kage):
    """Memory-efficient Kage for large datasets"""
    
    def __init__(self, *args, chunk_size: int = 1000, **kwargs):
        super().__init__(*args, **kwargs)
        self.chunk_size = chunk_size
    
    def process_streaming_data(self, data_stream: Iterator[Dict]) -> Iterator[Dict]:
        """Process data in chunks to minimize memory usage"""
        
        chunk = []
        for item in data_stream:
            chunk.append(item)
            
            if len(chunk) >= self.chunk_size:
                # Process chunk
                chunk_input = {"items": chunk}
                
                # Create temporary Kage for chunk
                temp_kage = Kage(chunk_input, self.input_schema, self.output_schema)
                
                # Copy function bindings
                for name, binding in self.functions.items():
                    temp_kage.functions[name] = binding
                
                # Execute chunk
                result = temp_kage.execute()
                yield result
                
                # Clear chunk and force garbage collection
                chunk.clear()
                del temp_kage
                gc.collect()
        
        # Process remaining items
        if chunk:
            chunk_input = {"items": chunk}
            temp_kage = Kage(chunk_input, self.input_schema, self.output_schema)
            
            for name, binding in self.functions.items():
                temp_kage.functions[name] = binding
            
            result = temp_kage.execute()
            yield result

# Usage for large datasets
def process_large_dataset():
    def data_generator():
        # Simulate large dataset
        for i in range(10000):
            yield {"id": i, "value": i * 2, "category": f"cat_{i % 10}"}
    
    streaming_kage = StreamingKage({}, {}, chunk_size=500)
    
    def process_chunk(items):
        return {
            "count": len(items),
            "sum_values": sum(item["value"] for item in items),
            "categories": list(set(item["category"] for item in items))
        }
    
    streaming_kage.bind_function(
        process_chunk,
        {"items": "items"},
        output_key="chunk_result"
    )
    
    # Process in chunks
    total_count = 0
    total_sum = 0
    all_categories = set()
    
    for chunk_result in streaming_kage.process_streaming_data(data_generator()):
        result = chunk_result["chunk_result"]
        total_count += result["count"]
        total_sum += result["sum_values"]
        all_categories.update(result["categories"])
    
    return {
        "total_items": total_count,
        "total_sum": total_sum,
        "unique_categories": len(all_categories)
    }
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Schema Validation Failures

**Problem:** `ValidationError: Type mismatch at user.age: expected integer, got str`

**Solution:**
```python
# Ensure data types match schema
input_data = {
    "user": {
        "age": 25  # Integer, not "25" (string)
    }
}

# Or use type conversion in functions
def convert_age(age_str):
    return int(age_str) if isinstance(age_str, str) else age_str
```

#### 2. Circular Dependencies

**Problem:** `ExecutionError: Circular or missing dependencies`

**Solution:**
```python
# Review dependency chains
kage.bind_function(func_a, {...}, dependencies=["func_c"])  # ✅
kage.bind_function(func_b, {...}, dependencies=["func_a"])  # ✅
kage.bind_function(func_c, {...})  # ✅ No dependencies

# Avoid circular references
# func_a depends on func_b, func_b depends on func_a ❌
```

#### 3. Function Parameter Mapping Issues

**Problem:** `KageError: Parameter 'user_id' not found in function 'process_user'`

**Solution:**
```python
# Check function signature
def process_user(user_id, user_name):  # Parameters must match mapping keys
    pass

# Correct mapping
kage.bind_function(
    process_user,
    {
        "user_id": "user.id",      # ✅ Matches function parameter
        "user_name": "user.name"   # ✅ Matches function parameter
    }
)
```

#### 4. Nested Data Access

**Problem:** `KageError: Input key 'user.profile.bio' not found in input data`

**Solution:**
```python
# Ensure nested structure exists
input_data = {
    "user": {
        "profile": {
            "bio": "User biography"  # ✅ Full path exists
        }
    }
}

# Or handle optional nested data
def safe_get_bio(user_data):
    return user_data.get("profile", {}).get("bio", "No bio available")
```

### Debug Mode

```python
class DebugKage(Kage):
    def __init__(self, *args, debug=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.debug = debug
    
    def execute(self):
        if self.debug:
            print(f"🚀 Starting execution with {len(self.functions)} functions")
            print(f"📋 Execution order: {self._resolve_execution_order()}")
        
        execution_order = self._resolve_execution_order()
        
        for func_name in execution_order:
            binding = self.functions[func_name]
            
            if self.debug:
                print(f"⚡ Executing: {func_name}")
                print(f"   Input mapping: {binding.input_mapping}")
                print(f"   Dependencies: {binding.dependencies}")
            
            try:
                # Prepare arguments
                kwargs = {}
                for param_name, input_key in binding.input_mapping.items():
                    if input_key in self.execution_results:
                        kwargs[param_name] = self.execution_results[input_key]
                    else:
                        kwargs[param_name] = self._get_nested_value(input_key, self.input_data)
                
                if self.debug:
                    print(f"   Arguments: {kwargs}")
                
                # Execute
                result = binding.func(**kwargs)
                self.execution_results[func_name] = result
                
                if self.debug:
                    print(f"   Result: {result}")
                
                # Update output
                if binding.output_key:
                    self._set_nested_value(binding.output_key, result, self.output_data)
                    if self.debug:
                        print(f"   Stored in output['{binding.output_key}']")
                
            except Exception as e:
                if self.debug:
                    print(f"❌ Error in {func_name}: {e}")
                raise ExecutionError(f"Error executing function '{func_name}': {str(e)}") from e
        
        if self.debug:
            print(f"✅ Execution completed successfully")
            print(f"📤 Final output keys: {list(self.output_data.keys())}")
        
        return self.output_data

# Usage
debug_kage = DebugKage(input_data, schema, debug=True)
# ... bind functions ...
result = debug_kage.execute()  # Will print detailed execution info
```

This comprehensive documentation covers all aspects of the Kage framework, from basic usage to advanced integration patterns. The framework is designed to be both simple for beginners and powerful enough for complex plugin architectures in production systems.