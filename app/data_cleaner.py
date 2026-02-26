import pandas as pd
from datetime import datetime
from typing import List, Dict, Tuple
import os

def normalize_sector(sector: str):
    if not sector or pd.isna(sector):
        return "unknown"
    return str(sector).strip().lower()

def parse_number(value):
    if value is None or pd.isna(value):
        return 0.0
    try:
        if isinstance(value, str):
            # Remove currency symbols and commas
            clean_val = value.replace(",", "").replace("$", "").strip()
            return float(clean_val)
        return float(value)
    except:
        return 0.0

def parse_date(value):
    if value is None or pd.isna(value):
        return None
    try:
        if isinstance(value, datetime):
            return value
        return pd.to_datetime(value).to_pydatetime()
    except:
        return None

def clean_deals_excel(file_path: str) -> Tuple[List[Dict], List[str]]:
    notes = []
    deals = []
    
    if not os.path.exists(file_path):
        return [], [f"Excel file not found: {os.path.basename(file_path)}"]

    try:
        df = pd.read_excel(file_path)
        # Actual columns from 'Deal funnel Data.xlsx'
        col_map = {
            'Deal Name': 'name',
            'Sector/service': 'sector',
            'Masked Deal value': 'amount',
            'Close Date (A)': 'close_date'
        }
        
        for _, row in df.iterrows():
            record = {}
            for excel_col, internal_key in col_map.items():
                if excel_col in df.columns:
                    record[internal_key] = row[excel_col]
            
            name = record.get('name', 'Unnamed Deal')
            sector = normalize_sector(record.get('sector'))
            amount = parse_number(record.get('amount'))
            close_date = parse_date(record.get('close_date'))

            if not record.get('amount'):
                # Only note if it's explicitly missing or 0 but expected
                pass 

            deals.append({
                "name": name,
                "sector": sector,
                "amount": amount,
                "close_date": close_date,
            })
        
        return deals, notes
    except Exception as e:
        return [], [f"Error reading Excel deals: {str(e)}"]

def clean_work_orders_excel(file_path: str) -> Tuple[List[Dict], List[str]]:
    orders = []
    if not os.path.exists(file_path):
        return [], [f"Excel file not found: {os.path.basename(file_path)}"]

    try:
        # Work orders has headers on the second row
        df = pd.read_excel(file_path, header=1)
        
        # Standardize keys for LLM analysis
        for _, row in df.iterrows():
            item = row.to_dict()
            # Map known columns to common names if they exist
            clean_item = {
                "name": item.get("Deal name masked", "Unnamed Task"),
                "status": item.get("Billing Status", "N/A"),
                "customer": item.get("Customer Name Code", "N/A")
            }
            orders.append(clean_item)
            
        return orders, []
    except Exception as e:
        return [], [f"Error reading Excel work orders: {str(e)}"]

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
        deals.append({"name": record["name"], "sector": sector, "amount": amount, "close_date": close_date})
    return deals, notes

def clean_work_orders(raw_data: Dict):
    try:
        return raw_data["data"]["boards"][0]["items_page"]["items"]
    except (KeyError, IndexError, TypeError):
        return []
