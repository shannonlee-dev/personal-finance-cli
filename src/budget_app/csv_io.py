"""거래 CSV 가져오기와 내보내기."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import TYPE_CHECKING

from .errors import AppError
from .models import Transaction
from .validators import (
    validate_date,
    validate_month,
)

if TYPE_CHECKING:
    from .services import BudgetService


def import_csv(service: BudgetService, source: Path) -> tuple[int, int]:
    imported = 0
    skipped = 0
    with source.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"date", "type", "category", "amount"}
        if not reader.fieldnames or not required.issubset(set(reader.fieldnames)):
            raise AppError(
                "CSV 헤더가 올바르지 않습니다.",
                "date,type,category,amount,memo,tags 헤더가 필요합니다.",
            )
        for row in reader:
            try:
                service.add_transaction(
                    tx_type=row.get("type", ""),
                    tx_date=row.get("date", ""),
                    amount=row.get("amount", ""),
                    category=row.get("category", ""),
                    memo=row.get("memo", "") or "",
                    tags=row.get("tags", "") or "",
                )
                imported += 1
            except AppError:
                skipped += 1
    return imported, skipped


def export_csv(
    service: BudgetService,
    target: Path,
    month: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
) -> int:
    if month:
        month = validate_month(month)
    elif not (date_from and date_to):
        raise AppError(
            "export 조건이 필요합니다.", "--month 또는 --from/--to를 지정하세요."
        )
    if date_from:
        date_from = validate_date(date_from)
    if date_to:
        date_to = validate_date(date_to)

    def include(tx: Transaction) -> bool:
        if month:
            return tx.date.startswith(month)
        return bool(date_from and date_to and date_from <= tx.date <= date_to)

    rows = [tx for tx in service.transactions.iter_all() if include(tx)]
    rows.sort(key=lambda tx: (tx.date, tx.id), reverse=True)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=["date", "type", "category", "amount", "memo", "tags"]
        )
        writer.writeheader()
        for tx in rows:
            writer.writerow(
                {
                    "date": tx.date,
                    "type": tx.type,
                    "category": tx.category,
                    "amount": tx.amount,
                    "memo": tx.memo,
                    "tags": ",".join(tx.tags),
                }
            )
    return len(rows)
