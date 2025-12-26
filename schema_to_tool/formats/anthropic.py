"""Anthropic tool format handler."""

from typing import Any


class AnthropicFormatter:
    """Formats tool definitions for Anthropic's tool use API."""

    @staticmethod
    def format(metadata: dict[str, Any]) -> dict[str, Any]:
        """Format tool metadata as Anthropic tool definition.

        Anthropic expects tools in this format:
        {
            "name": "tool_name",
            "description": "What the tool does",
            "input_schema": {
                "type": "object",
                "properties": {...},
                "required": [...]
            }
        }

        Args:
            metadata: Dictionary with name, description, and parameters.

        Returns:
            Anthropic-formatted tool definition.
        """
        return {
            "name": metadata["name"],
            "description": metadata["description"],
            "input_schema": metadata["parameters"],
        }

    @staticmethod
    def validate(tool: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate an Anthropic tool definition.

        Args:
            tool: Tool definition to validate.

        Returns:
            Tuple of (is_valid, list of error messages).
        """
        errors = []

        if not isinstance(tool, dict):
            return False, ["Tool must be a dictionary"]

        # Check required fields
        if "name" not in tool:
            errors.append("Tool must have a 'name' field")
        elif not isinstance(tool["name"], str):
            errors.append("Tool 'name' must be a string")
        elif not tool["name"]:
            errors.append("Tool 'name' cannot be empty")

        if "description" in tool and not isinstance(tool["description"], str):
            errors.append("Tool 'description' must be a string")

        if "input_schema" not in tool:
            errors.append("Tool must have an 'input_schema' field")
        elif not isinstance(tool["input_schema"], dict):
            errors.append("Tool 'input_schema' must be a dictionary")
        else:
            schema = tool["input_schema"]
            if schema.get("type") != "object":
                errors.append("Tool input_schema 'type' must be 'object'")
            if "properties" not in schema:
                errors.append("Tool input_schema must have 'properties'")

        return len(errors) == 0, errors

    @staticmethod
    def extract_schema(tool: dict[str, Any]) -> dict[str, Any]:
        """Extract the original schema from an Anthropic tool definition.

        Args:
            tool: Anthropic tool definition.

        Returns:
            JSON Schema extracted from the tool.
        """
        schema = {
            "name": tool.get("name", ""),
            "description": tool.get("description", ""),
        }
        input_schema = tool.get("input_schema", {})
        schema.update(input_schema)
        return schema
