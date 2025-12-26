"""OpenAI function calling format handler."""

from typing import Any


class OpenAIFormatter:
    """Formats tool definitions for OpenAI's function calling API."""

    @staticmethod
    def format(metadata: dict[str, Any]) -> dict[str, Any]:
        """Format tool metadata as OpenAI function definition.

        OpenAI expects tools in this format:
        {
            "type": "function",
            "function": {
                "name": "function_name",
                "description": "What the function does",
                "parameters": {
                    "type": "object",
                    "properties": {...},
                    "required": [...]
                }
            }
        }

        Args:
            metadata: Dictionary with name, description, and parameters.

        Returns:
            OpenAI-formatted tool definition.
        """
        return {
            "type": "function",
            "function": {
                "name": metadata["name"],
                "description": metadata["description"],
                "parameters": metadata["parameters"],
            },
        }

    @staticmethod
    def validate(tool: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate an OpenAI tool definition.

        Args:
            tool: Tool definition to validate.

        Returns:
            Tuple of (is_valid, list of error messages).
        """
        errors = []

        if not isinstance(tool, dict):
            return False, ["Tool must be a dictionary"]

        # Check top-level structure
        if tool.get("type") != "function":
            errors.append("Tool 'type' must be 'function'")

        if "function" not in tool:
            errors.append("Tool must have a 'function' field")
            return len(errors) == 0, errors

        func = tool["function"]

        # Check function structure
        if not isinstance(func, dict):
            errors.append("'function' must be a dictionary")
            return len(errors) == 0, errors

        if "name" not in func:
            errors.append("Function must have a 'name' field")
        elif not isinstance(func["name"], str):
            errors.append("Function 'name' must be a string")
        elif not func["name"]:
            errors.append("Function 'name' cannot be empty")

        if "description" in func and not isinstance(func["description"], str):
            errors.append("Function 'description' must be a string")

        if "parameters" not in func:
            errors.append("Function must have a 'parameters' field")
        elif not isinstance(func["parameters"], dict):
            errors.append("Function 'parameters' must be a dictionary")
        else:
            params = func["parameters"]
            if params.get("type") != "object":
                errors.append("Function parameters 'type' must be 'object'")
            if "properties" not in params:
                errors.append("Function parameters must have 'properties'")

        return len(errors) == 0, errors

    @staticmethod
    def extract_schema(tool: dict[str, Any]) -> dict[str, Any]:
        """Extract the original schema from an OpenAI tool definition.

        Args:
            tool: OpenAI tool definition.

        Returns:
            JSON Schema extracted from the tool.
        """
        func = tool.get("function", {})
        schema = {
            "name": func.get("name", ""),
            "description": func.get("description", ""),
        }
        params = func.get("parameters", {})
        schema.update(params)
        return schema
