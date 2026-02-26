import httpx
from app.config import MONDAY_API_TOKEN

MONDAY_API_URL = "https://api.monday.com/v2"


async def run_query(query: str):
    headers = {
        "Authorization": MONDAY_API_TOKEN,
        "Content-Type": "application/json",
        "API-Version": "2024-01"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            MONDAY_API_URL,
            json={"query": query},
            headers=headers,
        )
        response.raise_for_status()
        return response.json()


async def get_board_items(board_id: int):
    query = f"""
    query {{
      boards(ids: {board_id}) {{
        items_page(limit: 500) {{
          items {{
            id
            name
            column_values {{
              id
              text
              value
            }}
          }}
        }}
      }}
    }}
    """
    return await run_query(query)
