# Decision Log - Monday.com BI Agent

## 1. Tech Stack Selection
- **Framework**: FastAPI (Python)
  - *Rationale*: High performance, asynchronous (ideal for I/O bound API calls), and excellent integration with Pydantic for data validation.
- **LLM**: OpenAI GPT-4o
  - *Rationale*: Leading reasoning capabilities for intent classification and query planning.
- **Client**: `httpx`
  - *Rationale*: Provides asynchronous HTTP requests, essential for making concurrent calls to the monday.com API.
- **Data Handling**: Vanilla Python + Pydantic
  - *Rationale*: For the scale of "founder-level" queries, dedicated data-cleaning logic in Python is more readable and easier to debug than complex Pandas pipelines for small row counts.

## 2. Architectural Decisions
- **Live Queries**: Adhering to the "No Caching" requirement. Every user request triggers fresh GraphQL queries to ensure real-time accuracy for executive decisions.
- **Two-Tier Cleaning**: 
  - *Tier 1 (Normalization)*: Handling Monday.com's specific column structure (extracting `.text` vs `.value`).
  *Tier 2 (Domain Cleaning)*: Handling messy input (e.g., "$1,200" to `1200.0`, sector name normalization).
- **Visible Traces**: The agent returns a `tool_calls` list in the API response. This allows the UI to show exactly what boards were accessed, fulfilling the "Agent Action Visibility" requirement.

## 3. Resilience Strategy
- **Partial Success**: If one board fails to fetch but the other succeeds, the agent provides insights from the available data with a clear caveat.
- **Clarification Loop**: If the LLM identifies an ambiguous query (e.g., "Tell me about the energy sector" without specifying pipeline or work orders), it is programmed to ask for clarification.
