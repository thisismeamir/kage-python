## Usage Examples

### Example 1: Simple Data Processing

```python
from kage import core

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
from kage import core


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
from kage import core

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
from kage import core
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

