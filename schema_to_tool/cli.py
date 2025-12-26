"""CLI for schema-to-tool."""

import json
import sys
from pathlib import Path

import click

from schema_to_tool import __version__
from schema_to_tool.converter import SchemaConverter
from schema_to_tool.formats.openai import OpenAIFormatter
from schema_to_tool.formats.anthropic import AnthropicFormatter


@click.group()
@click.version_option(version=__version__, prog_name="schema-to-tool")
def cli():
    """Convert JSON Schema to OpenAI/Anthropic tool definitions."""
    pass


@cli.command()
@click.argument("schema_file", type=click.Path(exists=True))
@click.option(
    "--format",
    "-f",
    type=click.Choice(["openai", "anthropic"]),
    required=True,
    help="Output format for the tool definition.",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output file path. If not specified, prints to stdout.",
)
@click.option(
    "--indent",
    "-i",
    type=int,
    default=2,
    help="JSON indentation level (default: 2).",
)
def convert(schema_file: str, format: str, output: str | None, indent: int):
    """Convert a JSON Schema file to a tool definition.

    SCHEMA_FILE is the path to the JSON Schema file to convert.

    Examples:

        schema-to-tool convert schema.json --format openai

        schema-to-tool convert schema.json -f anthropic -o tool.json
    """
    try:
        converter = SchemaConverter.from_file(schema_file)
        result = converter.to_json(format, indent=indent)

        if output:
            output_path = Path(output)
            output_path.write_text(result)
            click.echo(f"Tool definition written to {output}")
        else:
            click.echo(result)

    except json.JSONDecodeError as e:
        click.echo(f"Error: Invalid JSON in schema file: {e}", err=True)
        sys.exit(1)
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("tool_file", type=click.Path(exists=True))
@click.option(
    "--format",
    "-f",
    type=click.Choice(["openai", "anthropic"]),
    required=True,
    help="Format of the tool definition to validate.",
)
def validate(tool_file: str, format: str):
    """Validate a tool definition file.

    TOOL_FILE is the path to the tool definition JSON file to validate.

    Examples:

        schema-to-tool validate tool.json --format openai

        schema-to-tool validate tool.json -f anthropic
    """
    try:
        with open(tool_file, "r") as f:
            tool = json.load(f)
    except json.JSONDecodeError as e:
        click.echo(f"Error: Invalid JSON: {e}", err=True)
        sys.exit(1)

    # Handle both single tool and array of tools
    tools = tool if isinstance(tool, list) else [tool]

    all_valid = True
    for i, t in enumerate(tools):
        if format == "openai":
            is_valid, errors = OpenAIFormatter.validate(t)
        elif format == "anthropic":
            is_valid, errors = AnthropicFormatter.validate(t)
        else:
            click.echo(f"Error: Unknown format: {format}", err=True)
            sys.exit(1)

        tool_name = ""
        if format == "openai" and isinstance(t, dict):
            tool_name = t.get("function", {}).get("name", f"tool[{i}]")
        elif format == "anthropic" and isinstance(t, dict):
            tool_name = t.get("name", f"tool[{i}]")
        else:
            tool_name = f"tool[{i}]"

        if is_valid:
            click.echo(f"[OK] {tool_name}: Valid {format} tool definition")
        else:
            all_valid = False
            click.echo(f"[ERROR] {tool_name}: Invalid {format} tool definition")
            for error in errors:
                click.echo(f"  - {error}")

    if all_valid:
        click.echo("\nAll tool definitions are valid.")
        sys.exit(0)
    else:
        click.echo("\nSome tool definitions have errors.", err=True)
        sys.exit(1)


def main():
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
