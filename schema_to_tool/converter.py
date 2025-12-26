"""Core conversion logic for JSON Schema to tool definitions."""

from typing import Any
import json


class SchemaConverter:
    """Converts JSON Schema to tool definitions for various AI platforms."""

    SUPPORTED_FORMATS = ["openai", "anthropic"]

    def __init__(self, schema: dict[str, Any]):
        """Initialize with a JSON Schema.

        Args:
            schema: A JSON Schema dictionary defining the tool parameters.
        """
        self.schema = schema
        self._validate_schema()

    def _validate_schema(self) -> None:
        """Validate that the schema has required fields."""
        if not isinstance(self.schema, dict):
            raise ValueError("Schema must be a dictionary")

    @classmethod
    def from_file(cls, filepath: str) -> "SchemaConverter":
        """Create a SchemaConverter from a JSON file.

        Args:
            filepath: Path to a JSON Schema file.

        Returns:
            SchemaConverter instance.
        """
        with open(filepath, "r") as f:
            schema = json.load(f)
        return cls(schema)

    @classmethod
    def from_json(cls, json_str: str) -> "SchemaConverter":
        """Create a SchemaConverter from a JSON string.

        Args:
            json_str: JSON Schema as a string.

        Returns:
            SchemaConverter instance.
        """
        schema = json.loads(json_str)
        return cls(schema)

    def _extract_tool_metadata(self) -> dict[str, Any]:
        """Extract tool metadata from schema.

        Returns:
            Dictionary with name, description, and parameters.
        """
        # If schema has a 'name' field at top level, use it as tool name
        name = self.schema.get("name", self.schema.get("title", "unnamed_tool"))

        # Get description from schema
        description = self.schema.get("description", "")

        # Build parameters schema
        if "properties" in self.schema:
            # Schema is directly a parameters object
            parameters = {
                "type": "object",
                "properties": self.schema.get("properties", {}),
            }
            if "required" in self.schema:
                parameters["required"] = self.schema["required"]
            if self.schema.get("additionalProperties") is not None:
                parameters["additionalProperties"] = self.schema["additionalProperties"]
        elif "parameters" in self.schema:
            # Schema already has parameters nested
            parameters = self.schema["parameters"]
        else:
            # Treat entire schema as parameters
            parameters = self.schema.copy()
            parameters.pop("name", None)
            parameters.pop("title", None)
            parameters.pop("description", None)
            if "type" not in parameters:
                parameters["type"] = "object"

        return {
            "name": self._normalize_name(name),
            "description": description,
            "parameters": parameters,
        }

    def _normalize_name(self, name: str) -> str:
        """Normalize a name to be a valid function name.

        Args:
            name: Original name.

        Returns:
            Normalized name with only alphanumeric and underscores.
        """
        # Replace spaces and hyphens with underscores
        normalized = name.replace(" ", "_").replace("-", "_")
        # Remove any characters that aren't alphanumeric or underscore
        normalized = "".join(c for c in normalized if c.isalnum() or c == "_")
        # Ensure it doesn't start with a number
        if normalized and normalized[0].isdigit():
            normalized = "_" + normalized
        return normalized or "unnamed_tool"

    def convert(self, format: str) -> dict[str, Any]:
        """Convert schema to the specified tool format.

        Args:
            format: Target format ('openai' or 'anthropic').

        Returns:
            Tool definition in the specified format.

        Raises:
            ValueError: If format is not supported.
        """
        if format not in self.SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported format: {format}. "
                f"Supported formats: {', '.join(self.SUPPORTED_FORMATS)}"
            )

        metadata = self._extract_tool_metadata()

        if format == "openai":
            from schema_to_tool.formats.openai import OpenAIFormatter

            return OpenAIFormatter.format(metadata)
        elif format == "anthropic":
            from schema_to_tool.formats.anthropic import AnthropicFormatter

            return AnthropicFormatter.format(metadata)

        raise ValueError(f"Unknown format: {format}")

    def to_json(self, format: str, indent: int = 2) -> str:
        """Convert schema to JSON string in the specified format.

        Args:
            format: Target format ('openai' or 'anthropic').
            indent: JSON indentation level.

        Returns:
            JSON string of the tool definition.
        """
        tool_def = self.convert(format)
        return json.dumps(tool_def, indent=indent)
