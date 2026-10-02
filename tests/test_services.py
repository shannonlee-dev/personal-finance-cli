"""분리한 저장소·CSV·반복 거래 사이의 실제 데이터 흐름을 검증한다."""

import pytest

from budget_app.errors import AppError
from budget_app.services import BudgetService


def test_recurring_clamps_month_end_and_does_not_repeat(tmp_path):
    service = BudgetService(tmp_path / "data")
    service.add_recurring("expense", 31, 20000, "rent", "월세", "정기")
    assert service.apply_recurring("2024-02") == 1
    tx = service.list_transactions(1)[0]
    assert tx.date == "2024-02-29" and tx.tags == ["정기"]
    assert service.apply_recurring("2024-02") == 0
    assert service.summary("2024-02", 3)["expense"] == 20000


def test_csv_skips_invalid_rows_and_round_trips(tmp_path):
    service = BudgetService(tmp_path / "data")
    source = tmp_path / "input.csv"
    source.write_text(
        "date,type,category,amount,memo,tags\n"
        "2024-01-01,expense,food,1000,점심,식사\n"
        "2024-01-02,expense,food,-1,잘못된 금액,\n",
        encoding="utf-8",
    )
    assert service.import_csv(source) == (1, 1)
    target = tmp_path / "export.csv"
    assert service.export_csv(target, month="2024-01") == 1
    other = BudgetService(tmp_path / "other")
    assert other.import_csv(target) == (1, 0)
    assert other.list_transactions(1)[0].memo == "점심"


def test_corrupt_storage_reports_line_without_rewriting(tmp_path):
    service = BudgetService(tmp_path)
    path = tmp_path / "transactions.jsonl"
    path.write_text('{"bad":\n', encoding="utf-8")
    original = path.read_bytes()
    with pytest.raises(AppError, match="transactions.jsonl:1"):
        service.list_transactions(20)
    assert path.read_bytes() == original


@pytest.mark.parametrize("limit", [0, -1])
def test_search_service_rejects_nonpositive_limit(tmp_path, limit):
    service = BudgetService(tmp_path)
    with pytest.raises(AppError, match="limit"):
        service.search_transactions(limit=limit)


def test_recurring_reference_prevents_category_deletion(tmp_path):
    service = BudgetService(tmp_path)
    service.add_category("subscription")
    service.add_recurring("expense", 5, 1000, "subscription")
    with pytest.raises(AppError, match="카테고리"):
        service.remove_category("subscription")
    assert "subscription" in service.categories()
    assert service.apply_recurring("2024-02") == 1


@pytest.mark.parametrize(
    "filters",
    [
        {"date_from": "2024-01-02", "date_to": "2024-01-02"},
        {"category": "food"},
        {"tx_type": "expense"},
        {"query": "LUNCH"},
        {"tag": "meal"},
        {"limit": 1},
    ],
)
def test_search_filters_exclude_nonmatching_transactions(tmp_path, filters):
    service = BudgetService(tmp_path)
    service.add_transaction("income", "2024-01-01", 5000, "salary", "Salary", "work")
    wanted = service.add_transaction(
        "expense", "2024-01-02", 1000, "food", "Lunch", "meal"
    )
    assert [tx.id for tx in service.search_transactions(**filters)] == [wanted.id]


def test_summary_totals_budget_and_expense_ranking(tmp_path):
    service = BudgetService(tmp_path)
    service.add_transaction("income", "2024-01-01", 5000, "salary")
    service.add_transaction("expense", "2024-01-02", 1000, "food")
    service.add_transaction("expense", "2024-01-03", 2000, "rent")
    service.add_transaction("expense", "2024-02-01", 9000, "rent")
    service.set_budget("2024-01", 2000)
    result = service.summary("2024-01", 1)
    assert (result["income"], result["expense"], result["balance"]) == (
        5000,
        3000,
        2000,
    )
    assert result["usage"] == 150 and result["over_budget"] is True
    assert result["top"] == [("rent", 2000)]
