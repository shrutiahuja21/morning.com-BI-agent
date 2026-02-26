from datetime import datetime


def filter_current_quarter(records):
    now = datetime.now()
    quarter = (now.month - 1) // 3 + 1

    filtered = []
    for r in records:
        if not r.get("close_date"):
            continue

        r_quarter = (r["close_date"].month - 1) // 3 + 1
        if r["close_date"].year == now.year and r_quarter == quarter:
            filtered.append(r)

    return filtered


def pipeline_by_sector(deals):
    result = {}
    for deal in deals:
        sector = deal.get("sector", "unknown")
        result.setdefault(sector, 0)
        result[sector] += deal.get("amount", 0)
    return result


def average_deal_size(deals):
    if not deals:
        return 0
    return sum(d.get("amount", 0) for d in deals) / len(deals)
