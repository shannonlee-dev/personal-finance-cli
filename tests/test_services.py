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
