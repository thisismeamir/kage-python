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

