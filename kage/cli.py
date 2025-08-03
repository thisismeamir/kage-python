# kage/cli.py
# !/usr/bin/env python3
"""
Kage CLI utilities and main function generator
"""

import json
import argparse
import sys
import os
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, Callable
from .node import KageNode, NodeValidationError
from .core import KageError, ValidationError, ExecutionError


def create_main_function(configure_func: Callable) -> Callable:
    """
    Creates a main function for Kage projects

    Args:
        configure_func: Function that takes a Kage instance and returns configured Kage

    Returns:
        Main function that can be called with sys.argv or used as entry point
    """

    def main(argv=None):
        """Generated main function for Kage node execution"""
        if argv is None:
            argv = sys.argv[1:]

        parser = argparse.ArgumentParser(description="Execute Kage Node")
        parser.add_argument("--input", required=True, help="Path to input JSON file")
        parser.add_argument("--working-dir", help="Working directory (optional)")
        parser.add_argument("--output-json", required=True, help="Path to output JSON file")
        parser.add_argument("--validate-only", action="store_true", help="Only validate, don't execute")
        parser.add_argument("--info", action="store_true", help="Show node information")

        args = parser.parse_args(argv)

        try:
            # Determine project directory
            project_dir = Path.cwd()
            if args.working_dir:
                os.chdir(args.working_dir)
                project_dir = Path(args.working_dir)

            # Initialize Kage node
            node = KageNode(project_dir)

            # Handle info request
            if args.info:
                info = node.get_info()
                print(json.dumps(info, indent=2))
                return 0

            # Validate node
            if not node.is_valid():
                print("Invalid Kage node", file=sys.stderr)
                return 1

            print(f"Valid Kage node: {node.node_config['name']} v{node.node_config['version']}")

            # Handle validation-only request
            if args.validate_only:
                print("Node validation passed")
                return 0

            # Load input data
            input_data = _load_input_data(Path(args.input))
            print(f"Loaded input data from {args.input}")

            # Initialize Kage
            kage = node.initialize_kage()
            print("Executing Kage node...")

            # Configure with user's function
            configured_kage = configure_func(kage)

            # Execute
            result = configured_kage.execute(input_data)

            # Save output
            _save_output_data(result, Path(args.output_json))
            print(f"Output saved to {args.output_json}")

            return 0

        except NodeValidationError as e:
            print(f"Node validation error: {e}", file=sys.stderr)
            _save_output_data({"error": e}, Path(args.output_json))
            return 1

        except ValidationError as e:
            _save_output_data({"error": e}, Path(args.output_json))
            return 1

        except ExecutionError as e:
            _save_output_data({"error": e}, Path(args.output_json))
            return 1

        except FileNotFoundError as e:
            _save_output_data({"error": e}, Path(args.output_json))
            return 1

        except Exception as e:
            _save_output_data({"error": e}, Path(args.output_json))
            return 1

    return main


def _load_input_data(input_file: Path) -> Dict[str, Any]:
    """Load input data from JSON file"""
    try:
        with open(input_file) as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in input file: {e}")
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {input_file}")


def _save_output_data(output_data: Dict[str, Any], output_file: Path):
    """Save output data to JSON file"""
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)


def init_project(project_name: str, template: str = "basic", target_dir: Optional[Path] = None):
    """
    Initialize a new Kage project

    Args:
        project_name: Name of the project
        template: Template to use (basic, advanced)
        target_dir: Target directory (defaults to current directory)
    """
    if target_dir is None:
        target_dir = Path.cwd() / project_name
    else:
        target_dir = Path(target_dir) / project_name

    # Create project directory
    target_dir.mkdir(parents=True, exist_ok=True)

    # Get template directory
    template_dir = Path(__file__).parent / "templates" / template
    if not template_dir.exists():
        raise ValueError(f"Template '{template}' not found")

    # Copy template files
    for file_path in template_dir.rglob("*"):
        if file_path.is_file():
            relative_path = file_path.relative_to(template_dir)
            target_path = target_dir / relative_path
            target_path.parent.mkdir(parents=True, exist_ok=True)

            # Replace placeholders in template files
            if file_path.suffix in ['.json', '.py', '.md']:
                content = file_path.read_text()
                content = content.replace("{{PROJECT_NAME}}", project_name)
                target_path.write_text(content)
            else:
                shutil.copy2(file_path, target_path)

    print(f"✅ Created Kage project '{project_name}' in {target_dir}")
    print(f"📁 Project structure:")
    for item in sorted(target_dir.rglob("*")):
        if item.is_file():
            relative = item.relative_to(target_dir)
            print(f"   {relative}")


def validate_project(project_dir: Optional[Path] = None):
    """Validate a Kage project"""
    if project_dir is None:
        project_dir = Path.cwd()

    try:
        node = KageNode(project_dir)
        info = node.get_info()

        if node.is_valid():
            print("✅ Valid Kage project")
            print(f"   Name: {info['name']}")
            print(f"   Version: {info['version']}")
            print(f"   Description: {info.get('description', 'N/A')}")
        else:
            print("❌ Invalid Kage project")

    except NodeValidationError as e:
        print(f"❌ Node validation error: {e}")
        return 1

    return 0


def main_cli():
    """Main CLI entry point for kage command"""
    parser = argparse.ArgumentParser(description="Kage Framework CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize new Kage project")
    init_parser.add_argument("name", help="Project name")
    init_parser.add_argument("--template", default="basic", choices=["basic", "advanced"],
                             help="Project template")
    init_parser.add_argument("--dir", type=Path, help="Target directory")

    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate Kage project")
    validate_parser.add_argument("--dir", type=Path, help="Project directory")

    # Version command
    subparsers.add_parser("version", help="Show version")

    args = parser.parse_args()

    if args.command == "init":
        try:
            init_project(args.name, args.template, args.dir)
            return 0
        except Exception as e:
            print(f"❌ Failed to create project: {e}", file=sys.stderr)
            return 1

    elif args.command == "validate":
        return validate_project(args.dir)

    elif args.command == "version":
        from . import __version__
        print(f"Kage Framework v{__version__}")
        return 0

    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main_cli())