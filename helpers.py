from glom import glom
from datetime import datetime


def _normalize_mbank_headers(headers):
    return [h.replace("#", "") for h in headers]


def _normalize_float(string):
    return float(string.strip().replace(",", ".").replace(" ", ""))


def report_balance(data):
    """Simple function returning income and spendings"""
    transactions = glom(data.dict, ["Kwota"])
    transactions = [_normalize_float(t) for t in transactions]

    expenses = sum(t for t in transactions if t < 0)
    income = sum(t for t in transactions if t > 0)
    balance = sum(transactions)

    return {"income": income, "expenses": expenses, "balance": balance}


def report_date(data):
    dts = glom(data.dict, [lambda d: datetime.strptime(d["Data operacji"], "%Y-%m-%d")])
    assert all((dt.year, dt.month) == (dts[0].year, dts[0].month) for dt in dts)
    return {"year": dts[0].year, "month": dts[0].month}


def last_balance(data):
    return _normalize_float(data.dict[-1]["Saldo po operacji"])


# @click.group(chain=True, invoke_without_command=True)
