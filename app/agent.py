import json
from openai import OpenAI
from typing import Dict, List, Optional
from app.config import OPENAI_API_KEY, BOARD_ID_DEALS, BOARD_ID_WORK_ORDERS
from app.monday_client import get_board_items
from app.data_cleaner import clean_deals, clean_work_orders
from app.analytics import pipeline_by_sector, filter_current_quarter, average_deal_size
from datetime import datetime

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# Memory stores query history as a list of strings for context
conversation_memory: Dict[str, List[str]] = {}

SYSTEM_PROMPT = """
You are a Business Intelligence Agent with a built-in 'Excel Fallback' feature.
Your goal: Answer founder-level business questions accurately using any available source (Monday.com Boards OR Local Excel Files).

Sources:
1. Monday.com (Live API): Always our first choice.
2. Excel Sheets (Fallback): Our redundant source.
   - 'Deal funnel Data.xlsx' handles sales/pipeline.
   - 'Work_Order_Tracker Data.xlsx' handles tasks/operations.

Routing Rules:
- If a Board ID is missing in the environment, you automatically use the Excel fallback.
- If you see data in 'Processed Data' (regardless of source), provide a detailed anlaysis.
- Mention if the data is from Excel fallback only if relevant for context, but focus on the INSIGHTS.
- Do NOT say 'I cannot access data' if you have data in the 'Processed Data' section.

Respond in JSON format:
{
  "needs_deals": boolean,
  "needs_work_orders": boolean,
  "requires_clarification": boolean,
  "clarification_message": string or null,
  "analysis_plan": "Strategy for analysis"
}
"""

def get_session_history(session_id: str) -> str:
    history = conversation_memory.get(session_id, [])
    return "\n".join(history[-5:]) # Last 5 exchanges

async def process_query(user_query: str, session_id: str):
    trace = []
    notes = []

    if not client:
        return {
            "answer": "OpenAI API key is missing. Please check your .env file.",
            "tool_calls": [],
            "data_quality_notes": ["System misconfiguration: No LLM available."]
        }

    history = get_session_history(session_id)
    
    # 1. LLM Intent Classification & Routing
    intent_response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"History:\n{history}\n\nQuery: {user_query}"}
        ],
        response_format={"type": "json_object"}
    )
    
    intent = json.loads(intent_response.choices[0].message.content)
    
    if intent.get("requires_clarification"):
        return {
            "answer": intent["clarification_message"],
            "tool_calls": ["LLM requested clarification"],
            "data_quality_notes": []
        }

    deals = []
    work_orders = []

    # 2. Data Fetching & Cleaning
    if intent["needs_deals"]:
        if BOARD_ID_DEALS:
            raw_deals = await get_board_items(BOARD_ID_DEALS)
            trace.append(f"Fetched Deals board (ID: {BOARD_ID_DEALS}) via live GraphQL API")
            deals, cleaning_notes = clean_deals(raw_deals)
            notes.extend(cleaning_notes)
            trace.append(f"Normalized {len(deals)} deal records")
        else:
            trace.append("BOARD_ID_DEALS not configured. Falling back to 'Deal funnel Data.xlsx'.")
            from app.data_cleaner import clean_deals_excel
            deals, excel_notes = clean_deals_excel("Deal funnel Data.xlsx")
            notes.extend(excel_notes)
            trace.append(f"Loaded {len(deals)} deal records from Excel.")

    if intent["needs_work_orders"]:
        if BOARD_ID_WORK_ORDERS:
            raw_wo = await get_board_items(BOARD_ID_WORK_ORDERS)
            trace.append(f"Fetched Work Orders board (ID: {BOARD_ID_WORK_ORDERS}) via live GraphQL API")
            work_orders = clean_work_orders(raw_wo)
            trace.append(f"Fetched {len(work_orders)} work order records")
        else:
            trace.append("BOARD_ID_WORK_ORDERS not configured. Falling back to 'Work_Order_Tracker Data.xlsx'.")
            from app.data_cleaner import clean_work_orders_excel
            work_orders, excel_notes = clean_work_orders_excel("Work_Order_Tracker Data.xlsx")
            notes.extend(excel_notes)
            trace.append(f"Loaded {len(work_orders)} work order records from Excel.")

    # 3. Analytics Processing (Simple filters based on typical queries)
    # Note: In a fuller implementation, the LLM could specify parameters for filter functions.
    if "quarter" in user_query.lower() or "current" in user_query.lower():
        deals = filter_current_quarter(deals)
        trace.append("Applied 'Current Quarter' filter to datasets")

    pipeline_insights = pipeline_by_sector(deals)
    avg_size = average_deal_size(deals)
    
    # Simple status distribution for Work Orders
    wo_status = {}
    for wo in work_orders:
        status = wo.get("status", "N/A")
        wo_status[status] = wo_status.get(status, 0) + 1
    
    analysis_results = {
        "pipeline_by_sector": pipeline_insights,
        "average_deal_size": avg_size,
        "total_deals_count": len(deals),
        "work_orders_count": len(work_orders),
        "work_order_status_distribution": wo_status
    }

    # 4. Final Answer Generation
    final_response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system", 
                "content": (
                    "You are a professional BI Analyst reporting to a company founder. "
                    "Your insights are based on raw data imported from Excel sheets into Monday.com. "
                    "Always mention data quality if 'Notes' are provided (e.g., missing amounts or messy formats). "
                    "Be decisive, professional, and highlight key trends in revenue or operations."
                )
            },
            {"role": "user", "content": f"User Query: {user_query}\n\nProcessed Data: {json.dumps(analysis_results)}\n\nData Quality Notes: {notes}"}
        ]
    )
    
    answer = final_response.choices[0].message.content

    # Update memory
    if session_id not in conversation_memory:
        conversation_memory[session_id] = []
    conversation_memory[session_id].append(f"User: {user_query}")
    conversation_memory[session_id].append(f"Agent: {answer}")

    return {
        "answer": answer,
        "tool_calls": trace,
        "data_quality_notes": notes,
    }
