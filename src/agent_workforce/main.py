import asyncio
from agents import Runner, set_tracing_disabled, enable_verbose_stdout_logging
from .config.settings import create_client, create_model
from .models.data_models import AnalysisContext
from .tools.function_tools import fetch_document
from .agents.agent_definitions import create_agents

# Initialize tracing and logging
set_tracing_disabled(disabled=True)
enable_verbose_stdout_logging()

# Create client and model
client = create_client()
model = create_model(client)

# Create all agents
agents = create_agents(model)
triage_agent = agents['triage_agent']

# Add fetch_document tool to triage agent (since it needs it)
triage_agent.tools.append(fetch_document)

async def main(document_id: str):
    context = AnalysisContext(document_id=document_id)
    result = await Runner.run(
        triage_agent,
        "Analyze the document with the given ID.",
        context=context
    )
    print(result.final_output)  # The DocumentAnalysis object

# Example usage
def start():
    asyncio.run(main("sample_invoice_id"))