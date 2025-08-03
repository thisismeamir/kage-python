## Integration Guide

### Integration with Flask Applications

```python
from flask import Flask, request, jsonify
from kage import core, ValidationError, ExecutionError

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
from kage import core, ValidationError, ExecutionError

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
