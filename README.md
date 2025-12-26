# schema-to-tool

Convert JSON Schema to OpenAI/Anthropic tool definitions.

## Installation

```bash
pip install schema-to-tool
```

Or install from source:

```bash
pip install -e .
```

## Usage

### Command Line

#### Convert JSON Schema to tool definition

```bash
# Convert to OpenAI function format
schema-to-tool convert schema.json --format openai

# Convert to Anthropic tool format
schema-to-tool convert schema.json --format anthropic

# Output to file
schema-to-tool convert schema.json -f openai -o tool.json

# Custom indentation
schema-to-tool convert schema.json -f anthropic -i 4
```

#### Validate tool definitions

```bash
# Validate OpenAI function definition
schema-to-tool validate tool.json --format openai

# Validate Anthropic tool definition
schema-to-tool validate tool.json --format anthropic
```

### Python API

```python
from schema_to_tool import SchemaConverter

# Create converter from schema dict
schema = {
    "name": "get_weather",
    "description": "Get the current weather for a location",
    "type": "object",
    "properties": {
        "location": {
            "type": "string",
            "description": "City and state, e.g. San Francisco, CA"
        },
        "unit": {
            "type": "string",
            "enum": ["celsius", "fahrenheit"],
            "description": "Temperature unit"
        }
    },
    "required": ["location"]
}

converter = SchemaConverter(schema)

# Convert to OpenAI format
openai_tool = converter.convert("openai")
print(openai_tool)
# {
#     "type": "function",
#     "function": {
#         "name": "get_weather",
#         "description": "Get the current weather for a location",
#         "parameters": {
#             "type": "object",
#             "properties": {...},
#             "required": ["location"]
#         }
#     }
# }

# Convert to Anthropic format
anthropic_tool = converter.convert("anthropic")
print(anthropic_tool)
# {
#     "name": "get_weather",
#     "description": "Get the current weather for a location",
#     "input_schema": {
#         "type": "object",
#         "properties": {...},
#         "required": ["location"]
#     }
# }

# Load from file
converter = SchemaConverter.from_file("schema.json")

# Get JSON string
json_str = converter.to_json("openai", indent=2)
```

### Validation

```python
from schema_to_tool.formats.openai import OpenAIFormatter
from schema_to_tool.formats.anthropic import AnthropicFormatter

# Validate OpenAI tool
is_valid, errors = OpenAIFormatter.validate(openai_tool)
if not is_valid:
    print("Errors:", errors)

# Validate Anthropic tool
is_valid, errors = AnthropicFormatter.validate(anthropic_tool)
```

## Schema Format

The converter accepts JSON Schema with the following structure:

```json
{
    "name": "function_name",
    "description": "What the function does",
    "type": "object",
    "properties": {
        "param1": {
            "type": "string",
            "description": "Parameter description"
        }
    },
    "required": ["param1"]
}
```

The `name` field can also be specified as `title`. If neither is provided, the tool will be named `unnamed_tool`.

## Output Formats

### OpenAI

```json
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
```

### Anthropic

```json
{
    "name": "function_name",
    "description": "What the function does",
    "input_schema": {
        "type": "object",
        "properties": {...},
        "required": [...]
    }
}
```

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black schema_to_tool
ruff check schema_to_tool --fix
```

## License

MIT
