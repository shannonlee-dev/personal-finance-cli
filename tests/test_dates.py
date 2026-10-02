"""비정규 입력과 기존 JSONL 데이터도 같은 월·기간으로 집계한다."""

import csv
import json

from budget_app.services import BudgetService


def test_new_transaction_is_canonical_and_visible_in_monthly_summary(tmp_path):
    service = BudgetService(tmp_path)
    tx = service.add_transaction("expense", "2024-1-5", 1000, "food")
    assert tx.date == "2024-01-05"
    assert service.summary("2024-01", 3)["expense"] == 1000


def test_legacy_dates_and_budgets_are_read_without_rewriting(tmp_path):
    service = BudgetService(tmp_path)
    transactions = tmp_path / "transactions.jsonl"
    transactions.write_text(
        json.dumps(
            {
                "id": "TX-000001",
                "date": "2024-1-5",
                "type": "expense",
                "category": "food",
                "amount": 1000,
            }
        )
        + "\n"
    )
    budgets = tmp_path / "budgets.jsonl"
    budgets.write_text('{"month":"2024-1","amount":10000}\n')
    originals = transactions.read_bytes(), budgets.read_bytes()
    result = service.summary("2024-01", 3)
    assert result["expense"] == 1000 and result["budget"] == 10000
    assert result["usage"] == 10.0
    assert service.list_transactions(1)[0].date == "2024-01-05"
    assert (transactions.read_bytes(), budgets.read_bytes()) == originals


def test_month_input_is_canonical_for_budgets_and_recurring(tmp_path):
    service = BudgetService(tmp_path)
    service.set_budget("2024-1", 10000)
    assert service.summary("2024-01", 3)["budget"] == 10000
    assert json.loads((tmp_path / "budgets.jsonl").read_text())["month"] == "2024-01"
    service.add_recurring("expense", 5, 1000, "food")
    assert service.apply_recurring("2024-2") == 1
    assert service.apply_recurring("2024-02") == 0
    assert service.list_transactions(1)[0].date == "2024-02-05"


def test_search_and_export_use_canonical_date_ranges(tmp_path):
    service = BudgetService(tmp_path)
    service.add_transaction("expense", "2024-01-05", 1000, "food")
    assert (
        len(service.search_transactions(date_from="2024-1-1", date_to="2024-1-9")) == 1
    )
    target = tmp_path / "out.csv"
    assert service.export_csv(target, date_from="2024-1-1", date_to="2024-1-9") == 1
    with target.open() as handle:
        assert list(csv.DictReader(handle))[0]["date"] == "2024-01-05"


def test_csv_import_normalizes_dates_for_monthly_export(tmp_path):
    service = BudgetService(tmp_path / "data")
    source = tmp_path / "in.csv"
    source.write_text("date,type,category,amount\n2024-1-5,expense,food,1000\n")
    assert service.import_csv(source) == (1, 0)
    assert service.export_csv(tmp_path / "out.csv", month="2024-01") == 1
