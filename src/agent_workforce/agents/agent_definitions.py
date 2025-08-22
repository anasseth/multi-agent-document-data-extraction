from agents import Agent, OpenAIChatCompletionsModel, handoff
from ..models.data_models import AnalysisContext, Classification
from ..tools.function_tools import get_page_content
from ..prompts.agent_prompts import (
    INVOICE_PAGE_EXTRACTOR_PROMPT,
    GENERAL_PAGE_EXTRACTOR_PROMPT,
    INVOICE_EXTRACTOR_PROMPT,
    GENERAL_EXTRACTOR_PROMPT,
    TRIAGE_AGENT_PROMPT,
    UI_TRANSFORMATION_PROMPT
)

def create_agents(model: OpenAIChatCompletionsModel):
    """Create and return all agent instances"""
    
    page_extractor_invoice = Agent[AnalysisContext](
        name="InvoicePageExtractor",
        instructions=INVOICE_PAGE_EXTRACTOR_PROMPT,
        tools=[get_page_content],
        model=model
    )
    
    ui_transformation_agent = Agent[AnalysisContext](
        name="UITransformer",
        instructions=UI_TRANSFORMATION_PROMPT,
        tools=[],
        model=model
    )

    invoice_agent = Agent[AnalysisContext](
        name="InvoiceExtractor",
        instructions=INVOICE_EXTRACTOR_PROMPT,
        tools=[
            page_extractor_invoice.as_tool(
                tool_name="extract_page",
                tool_description="Extract sections from a page of the invoice. Input is the page number as string."
            )
        ],
        handoffs=[
            handoff(
                agent=ui_transformation_agent,
                tool_name_override="transform_to_ui_format",
                input_type=AnalysisContext,
                on_handoff=on_handoff_to_ui
            )
        ],
        model=model
    )

    general_page_extractor = Agent[AnalysisContext](
        name="GeneralPageExtractor",
        instructions=GENERAL_PAGE_EXTRACTOR_PROMPT,
        tools=[get_page_content],
        model=model
    )

    general_agent = Agent[AnalysisContext](
        name="GeneralExtractor",
        instructions=GENERAL_EXTRACTOR_PROMPT,
        tools=[
            general_page_extractor.as_tool(
                tool_name="extract_page",
                tool_description="Extract sections from a page. Input is page number as string."
            )
        ],
        handoffs=[
            handoff(
                agent=ui_transformation_agent,
                tool_name_override="transform_to_ui_format",
                input_type=AnalysisContext,
                on_handoff=on_handoff_to_ui
            )
        ],
        model=model
    )

    triage_agent = Agent[AnalysisContext](
        name="DocumentTriage",
        instructions=TRIAGE_AGENT_PROMPT,
        tools=[get_page_content],
        handoffs=[
            handoff(
                agent=invoice_agent,
                tool_name_override="transfer_to_invoice_extractor",
                input_type=Classification,
                on_handoff=on_handoff_common
            ),
            handoff(
                agent=general_agent,
                tool_name_override="transfer_to_general_extractor",
                input_type=Classification,
                on_handoff=on_handoff_common
            ),
        ],
        model=model
    )
    
    return {
        'page_extractor_invoice': page_extractor_invoice,
        'invoice_agent': invoice_agent,
        'general_page_extractor': general_page_extractor,
        'general_agent': general_agent,
        'ui_transformation_agent': ui_transformation_agent,
        'triage_agent': triage_agent
    }

def on_handoff_common(ctx, input_data: Classification):
    """Common handoff handler"""
    ctx.context.document_type = input_data.document_type
    ctx.context.high_level_type = input_data.document_high_level_type
    ctx.context.total_pages = input_data.total_pages

def on_handoff_to_ui(ctx, input_data: AnalysisContext):
    """Handler for handoff to UI transformation agent"""
    pass
