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
