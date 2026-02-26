from datetime import datetime
from typing import List, Dict, Tuple


def normalize_sector(sector: str):
    if not sector:
        return "unknown"
    return sector.strip().lower()


def parse_number(value):
    if not value:
        return 0.0
    try:
        if isinstance(value, str):
            return float(value.replace(",", "").replace("$", ""))
        return float(value)
    except:
        return 0.0


def parse_date(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except:
        try:
            # Handle some common alternative formats
            return datetime.strptime(value, "%Y-%m-%d")
        except:
            return None


def clean_deals(raw_data: Dict) -> Tuple[List[Dict], List[str]]:
    notes = []
    deals = []

    try:
        items = raw_data["data"]["boards"][0]["items_page"]["items"]
    except (KeyError, IndexError, TypeError):
        return [], ["Failed to parse deals board structure"]

    for item in items:
        record = {"name": item["name"]}
        for col in item["column_values"]:
            record[col["id"]] = col["text"]

        sector = normalize_sector(record.get("sector"))
        amount = parse_number(record.get("amount"))
        close_date = parse_date(record.get("close_date"))

        if not record.get("amount"):
            notes.append(f"Deal '{record['name']}' missing amount; treated as 0.")

        deals.append(
            {
                "name": record["name"],
                "sector": sector,
                "amount": amount,
                "close_date": close_date,
            }
        )

    return deals, notes


def clean_work_orders(raw_data: Dict):
    try:
        return raw_data["data"]["boards"][0]["items_page"]["items"]
    except (KeyError, IndexError, TypeError):
        return []
