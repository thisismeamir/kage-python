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
from kage import core, ValidationError


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

