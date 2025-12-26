"""Schema to Tool - Convert JSON Schema to OpenAI/Anthropic tool definitions."""

__version__ = "0.1.0"

from schema_to_tool.converter import SchemaConverter
from schema_to_tool.formats.openai import OpenAIFormatter
from schema_to_tool.formats.anthropic import AnthropicFormatter

__all__ = ["SchemaConverter", "OpenAIFormatter", "AnthropicFormatter", "__version__"]
