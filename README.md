# Monday.com Business Intelligence Agent

A production-ready AI agent that interprets "founder-level" business questions and provides insights by querying live Monday.com boards (Deals & Work Orders).

## 🌟 Features

- **Live Monday.com Integration**: No caching. Fetches real-time data using the Monday.com GraphQL API.
- **LLM Query Routing**: Uses GPT-4o to classify user intent, plan analysis, and decide which boards to query.
- **Data Normalization**: Robust cleaning logic for "messy" data (handles irregular currency formats, dates, and missing fields).
- **Conversational Memory**: Supports follow-up questions within the same session.
- **Action Trace Visibility**: Transparent reporting of API calls and data cleaning steps taken by the agent.
- **Premium UI**: A sleek, dark-themed glassmorphism interface for seamless interaction.

## 📁 Project Structure

```text
monday-bi-agent/
├── app/                    # Backend (FastAPI)
│   ├── main.py             # Entry point with CORS
│   ├── agent.py            # LLM Routing & Reasoning
│   ├── monday_client.py    # GraphQL API interactions
│   ├── data_cleaner.py     # Data normalization
│   ├── analytics.py        # BI calculation logic
│   ├── models.py           # Pydantic Schemas
│   └── config.py           # Env management
├── frontend/               # Premium Web Interface
│   ├── index.html          # Chat interface
│   ├── css/style.css       # Custom styling
│   └── js/app.js           # API integration
├── .env.example            # Environment template
├── DECISION_LOG.md         # Technical architecture justification
└── requirements.txt        # Python dependencies
```

## 🚀 Setup & Installation

### 1. Prerequisites
- Python 3.9+
- Monday.com API Token
- OpenAI API Key

### 2. Configure Environment
Create a `.env` file in the root directory and fill in your details:
```bash
OPENAI_API_KEY=your_key_here
MONDAY_API_TOKEN=your_token_here
BOARD_ID_DEALS=123456789
BOARD_ID_WORK_ORDERS=987654321
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Start the Application

**Run the Backend:**
```bash
uvicorn app.main:app --reload
```
The API will be available at `http://localhost:8000`.

**Open the Frontend:**
Open `frontend/index.html` in your favorite web browser.

## 📊 Sample Queries
- "How is our energy pipeline looking for this quarter?"
- "What is the average deal size across all sectors?"
- "Are there any urgent work orders?"
- "Give me a summary of the tech sector revenue." (Follow-up: "What about the retail sector?")

## 🛠 Technical Decisions
Refer to [DECISION_LOG.md](./DECISION_LOG.md) for detailed reasoning on the tech stack and architectural choices.
