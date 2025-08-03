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
