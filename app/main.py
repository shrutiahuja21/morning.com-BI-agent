from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.agent import process_query
from app.models import QueryRequest

app = FastAPI(title="Monday BI Agent")

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/query")
async def query_agent(request: QueryRequest):
    result = await process_query(request.query, request.session_id)
    return result


@app.get("/")
def health():
    return {"status": "running"}
