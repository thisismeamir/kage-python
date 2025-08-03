#!/usr/bin/env python3
"""
Kage Node System - main.py
Standard entry point for Kage-based projects
"""

import json
import argparse
import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional
from kage.core import Kage, KageError, ValidationError, ExecutionError


class NodeValidationError(Exception):
    """Raised when .node.json validation fails"""
    pass


class KageNode:
    """
    Kage Node - Validates and executes Kage-based projects
    """

    NODE_SCHEMA = {
        "type": "object",
        "required": ["name", "version", "type", "model"],
        "properties": {
            "name": "string",
            "version": "string",
            "type": "string",
            "model": {
                "type": "object",
                "required": ["execution_model", "source", "entry_file"],
                "properties": {
                    "execution_model": {
                        "type": "object",
                        "required": ["language", "input_schema", "output_schema"],
                        "properties": {
                            "language": "string",
                            "input_schema": "object",
                            "output_schema": "object",
                            "artifacts": {
                                "type": "array",
                                "items": "string"
                            }
                        }
                    },
                    "source": "string",
                    "working_directory": "string",
                    "entry_file": "string",
                    "output_directory": "string"
                }
            },
            "metadata": {
                "type": "object",
                "properties": {
                    "description": "string",
                    "authors": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": "string",
                                "email": "string",
                                "url": "string"
                            }
                        }
                    },
                    "manual": "string",
                    "repository": "string"
                }
            }
        }
    }

    def __init__(self, project_dir: Path):
        self.project_dir = Path(project_dir)
        self.node_config = self._load_node_config()
        self.kage: Optional[Kage] = None

    def _load_node_config(self) -> Dict[str, Any]:
        """Load and validate .node.json configuration"""
        node_file = next(self.project_dir.glob("*.node.json"), None)

        if not node_file.exists():
            raise NodeValidationError(f".node.json not found in {self.project_dir}")

        try:
            with open(node_file) as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            raise NodeValidationError(f"Invalid JSON in .node.json: {e}")

        # Validate node config structure
        try:
            temp_kage = Kage(config, self.NODE_SCHEMA)
        except ValidationError as e:
            raise NodeValidationError(f"Invalid .node.json structure: {e}")

        return config

    def is_valid(self) -> bool:
        """Check if this is a valid Kage node"""
        try:
            # Check required files exist
            entry_file = self.project_dir / self.node_config["model"]["entry_file"]
            if not entry_file.exists():
                return False

            # Check if it's a proper Kage node type
            if self.node_config.get("type") != "node":
                return False

            # Check if language is Python
            if self.node_config["model"]["execution_model"]["language"] != "python":
                return False

            return True

        except Exception:
            return False

    def get_input_schema(self) -> Dict[str, Any]:
        """Get input schema from node config"""
        return self.node_config["model"]["execution_model"]["input_schema"]

    def get_output_schema(self) -> Dict[str, Any]:
        """Get output schema from node config"""
        return self.node_config["model"]["execution_model"]["output_schema"]

    def initialize_kage(self) -> Kage:
        """Initialize Kage instance with input data and schemas"""
        try:
            self.kage = Kage(
                self.get_input_schema(),
                self.get_output_schema()
            )
            return self.kage

        except ValidationError as e:
            raise KageError(f"Input validation failed: {e}")

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the Kage node"""
        if not self.kage:
            self.initialize_kage()

        return self.kage.execute(input_data)

    def get_info(self) -> Dict[str, Any]:
        """Get node information"""
        return {
            "name": self.node_config["name"],
            "version": self.node_config["version"],
            "description": self.node_config.get("metadata", {}).get("description", ""),
            "valid": self.is_valid(),
            "input_schema": self.get_input_schema(),
            "output_schema": self.get_output_schema()
        }


def load_input_data(input_file: Path) -> Dict[str, Any]:
    """Load input data from JSON file"""
    try:
        with open(input_file) as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in input file: {e}")
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {input_file}")


def save_output_data(output_data: Dict[str, Any], output_file: Path):
    """Save output data to JSON file"""
    # Ensure output directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)


def main():
    """Main entry point for Kage node execution"""
    parser = argparse.ArgumentParser(description="Execute Kage Node")
    parser.add_argument("--input", required=True, help="Path to input JSON file")
    parser.add_argument("--working-dir", help="Working directory (optional)")
    parser.add_argument("--output-json", required=True, help="Path to output JSON file")
    parser.add_argument("--validate-only", action="store_true", help="Only validate, don't execute")
    parser.add_argument("--info", action="store_true", help="Show node information")

    args = parser.parse_args()

    try:
        # Determine project directory
        project_dir = Path(__file__).parent
        if args.working_dir:
            os.chdir(args.working_dir)

        # Initialize Kage node
        node = KageNode(project_dir)

        # Handle info request
        if args.info:
            info = node.get_info()
            print(json.dumps(info, indent=2))
            return 0

        # Validate node
        if not node.is_valid():
            print("❌ Invalid Kage node", file=sys.stderr)
            return 1

        print(f"✅ Valid Kage node: {node.node_config['name']} v{node.node_config['version']}")

        # Handle validation-only request
        if args.validate_only:
            print("✅ Node validation passed")
            return 0

        # Load input data
        input_data = load_input_data(Path(args.input))
        print(f"📥 Loaded input data from {args.input}")

        # Initialize and execute Kage
        node.initialize_kage()
        print("🚀 Executing Kage node...")

        # Import and configure the actual plugin
        # This is where your specific plugin logic would be imported
        plugin_module = __import__("plugin")  # Assumes plugin.py exists
        if hasattr(plugin_module, 'configure_kage'):
            node.kage = plugin_module.configure_kage(node.kage)
        else:
            raise KageError("Plugin must implement configure_kage(kage) function")

        # Execute
        result = node.execute(input_data)

        # Save output
        save_output_data(result, Path(args.output_json))
        print(f"📤 Output saved to {args.output_json}")

        return 0

    except NodeValidationError as e:
        print(f"❌ Node validation error: {e}", file=sys.stderr)
        return 1

    except ValidationError as e:
        print(f"❌ Input validation error: {e}", file=sys.stderr)
        return 1

    except ExecutionError as e:
        print(f"❌ Execution error: {e}", file=sys.stderr)
        return 1

    except FileNotFoundError as e:
        print(f"❌ File error: {e}", file=sys.stderr)
        return 1

    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())




# Validation utility functions
def validate_kage_project(project_dir: Path) -> Dict[str, Any]:
    """
    Utility function to validate a Kage project
    Returns validation results
    """
    results = {
        "valid": False,
        "errors": [],
        "warnings": [],
        "info": {}
    }

    try:
        node = KageNode(project_dir)
        results["valid"] = node.is_valid()
        results["info"] = node.get_info()

        # Additional checks
        plugin_file = project_dir / "plugin.py"
        if not plugin_file.exists():
            results["errors"].append("plugin.py not found")

        main_file = project_dir / "main.py"
        if not main_file.exists():
            results["warnings"].append("main.py not found (using default)")

    except NodeValidationError as e:
        results["errors"].append(str(e))
    except Exception as e:
        results["errors"].append(f"Unexpected error: {e}")

    return results


