import asyncio
from agents import Runner, set_tracing_disabled, enable_verbose_stdout_logging
from .config.settings import create_client, create_model
from .models.data_models import AnalysisContext
from .tools.function_tools import fetch_document, get_complete_analysis
from .agents.agent_definitions import create_agents

set_tracing_disabled(disabled=True)
enable_verbose_stdout_logging()

client = create_client()
model = create_model(client)

agents = create_agents(model)
triage_agent = agents['triage_agent']

triage_agent.tools.append(fetch_document)

async def main(document_id: str):
    context = AnalysisContext(document_id=document_id)
    result = await Runner.run(
        triage_agent,
        "Analyze the document with the given ID and provide both original extracted data and UI-compatible format using the agent-based transformation workflow.",
        context=context
    )
    print("=== FINAL OUTPUT ===")
    print(result.final_output)
    
    # The result contains both original and UI-compatible data
    # - result.final_output: Complete analysis with both formats
    # - context.original_analysis: Raw extracted data
    # - context.ui_analysis: UI-compatible format
    
    return result

def start():
    asyncio.run(main("sample_invoice_id"))