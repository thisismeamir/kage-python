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