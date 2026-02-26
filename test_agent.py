import asyncio
from app.agent import process_query

async def main():
    print("Testing query: 'Show me the pipeline summary'")
    result = await process_query("Show me the pipeline summary", "test_session")
    print(f"\nANSWER:\n{result['answer']}")
    print(f"\nTRACE:\n{result['tool_calls']}")
    print(f"\nNOTES:\n{result['data_quality_notes']}")

if __name__ == "__main__":
    asyncio.run(main())
