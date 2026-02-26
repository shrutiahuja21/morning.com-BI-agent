import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MONDAY_API_TOKEN = os.getenv("MONDAY_API_TOKEN")

# Safely convert to int if present, else None
def get_int_env(key):
    val = os.getenv(key)
    try:
        return int(val) if val else None
    except ValueError:
        return None

BOARD_ID_DEALS = get_int_env("BOARD_ID_DEALS")
BOARD_ID_WORK_ORDERS = get_int_env("BOARD_ID_WORK_ORDERS")
