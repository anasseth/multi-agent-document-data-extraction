# Agent Workforce - Modular Structure

This directory contains the modularized version of the agent workforce system, broken down into logical components for better maintainability and organization.

## Directory Structure

```
src/agent_workforce/
├── __init__.py
├── main.py                 # Main entry point (simplified)
├── README.md              # This file
├── test_imports.py        # Test script for imports
├── config/                # Configuration and settings
│   ├── __init__.py
│   └── settings.py        # API keys, URLs, client creation
├── models/                # Data models and classes
│   ├── __init__.py
│   └── data_models.py     # AnalysisContext, Classification, etc.
├── tools/                 # Function tools
│   ├── __init__.py
│   └── function_tools.py  # fetch_document, get_page_content
├── prompts/               # Agent instruction prompts
│   ├── __init__.py
│   └── agent_prompts.py   # All agent instructions
└── agents/                # Agent definitions
    ├── __init__.py
    └── agent_definitions.py # All agent instances
```

## Key Benefits

1. **Separation of Concerns**: Each component has a specific responsibility
2. **Maintainability**: Easier to locate and modify specific functionality
3. **Reusability**: Components can be imported and used independently
4. **Testing**: Individual components can be tested in isolation
5. **Scalability**: Easy to add new agents, tools, or models

## Components

### Config (`config/settings.py`)

- API configuration
- Client and model creation functions
- Environment-specific settings

### Models (`models/data_models.py`)

- `AnalysisContext`: Runtime context for document analysis
- `Classification`: Document type classification
- `DocumentAnalysis`: Final analysis output structure
- `DocumentMeta` and `Page`: Supporting data structures

### Tools (`tools/function_tools.py`)

- `fetch_document`: Fetches and parses PDF documents
- `get_page_content`: Retrieves content from specific pages

### Prompts (`prompts/agent_prompts.py`)

- All agent instruction strings
- Centralized prompt management
- Easy to modify and version control

### Agents (`agents/agent_definitions.py`)

- Agent creation and configuration
- Handoff logic
- Tool assignments

### Main (`main.py`)

- Entry point
- Orchestration logic
- Minimal, focused on workflow

## Usage

The main entry point remains the same:

```python
from agent_workforce.main import start

# Start the document analysis
start()
```

## Testing

Run the test script to verify all imports work:

```bash
cd src/agent_workforce
python -m test_imports
```

## Adding New Components

1. **New Agent Type**: Add to `agents/agent_definitions.py`
2. **New Tool**: Add to `tools/function_tools.py`
3. **New Model**: Add to `models/data_models.py`
4. **New Prompt**: Add to `prompts/agent_prompts.py`

## Notes

- All original logic has been preserved
- No functional changes were made
- The system maintains the same external interface
- Import paths use relative imports for package structure
