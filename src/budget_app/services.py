from __future__ import annotations

import heapq
from dataclasses import replace
from pathlib import Path

from . import csv_io, recurring
from .errors import AppError
from .models import RecurringRule, Transaction
from .repository import TransactionRepository
from .storage import JsonlStore
from .validators import (
    parse_tags,
    validate_amount,
    validate_date,
    validate_month,
    validate_type,
)


class BudgetService:
    def __init__(self, data_dir: Path) -> None:
        self.store = JsonlStore(data_dir)
        self.transactions = TransactionRepository(self.store)
        self.store.ensure()

    def require_category(self, category: str) -> str:
        category = category.strip()
        if not category:
            raise AppError(
                "카테고리가 비어 있습니다.",
                "category list로 사용 가능한 값을 확인하세요.",
            )
        if category not in self.store.categories():
            raise AppError(
                "등록되지 않은 카테고리입니다.",
                f"category add {category}로 먼저 등록하세요.",
            )
        return category

    def add_transaction(
        self,
        tx_type: str,
        tx_date: str,
        amount: str | int,
        category: str,
        memo: str = "",
        tags: str | None = None,
    ) -> Transaction:
        tx = Transaction(
            id=self.store.next_transaction_id(),
            type=validate_type(tx_type),
            date=validate_date(tx_date),
            amount=validate_amount(amount),
            category=self.require_category(category),
            memo=memo,
            tags=parse_tags(tags),
        )
        self.transactions.add(tx)
        return tx

    def list_transactions(self, limit: int) -> list[Transaction]:
        return heapq.nlargest(
            limit, self.transactions.iter_all(), key=lambda tx: (tx.date, tx.id)
        )

    def search_transactions(
        self,
        date_from: str | None = None,
        date_to: str | None = None,
        category: str | None = None,
        tx_type: str | None = None,
        query: str | None = None,
        tag: str | None = None,
        limit: int = 100,
    ) -> list[Transaction]:
        if date_from:
            date_from = validate_date(date_from)
        if date_to:
            date_to = validate_date(date_to)
        if tx_type:
            tx_type = validate_type(tx_type)
        if category:
            self.require_category(category)
        query_lower = query.lower() if query else None

        def matches(tx: Transaction) -> bool:
            if date_from and tx.date < date_from:
                return False
            if date_to and tx.date > date_to:
                return False
            if category and tx.category != category:
                return False
            if tx_type and tx.type != tx_type:
                return False
            if query_lower and query_lower not in tx.memo.lower():
                return False
            if tag and tag not in tx.tags:
                return False
            return True

        return heapq.nlargest(
            limit,
            (tx for tx in self.transactions.iter_all() if matches(tx)),
            key=lambda tx: (tx.date, tx.id),
        )

    def set_budget(self, month: str, amount: str | int) -> None:
        self.store.set_budget(validate_month(month), validate_amount(amount))

    def summary(self, month: str, top: int) -> dict[str, object]:
        month = validate_month(month)
        income = 0
        expense = 0
        by_category: dict[str, int] = {}
        sample_count = 0
        for tx in self.transactions.iter_all():
            if not tx.date.startswith(month):
                continue
            sample_count += 1
            if tx.type == "income":
                income += tx.amount
            else:
                expense += tx.amount
                by_category[tx.category] = by_category.get(tx.category, 0) + tx.amount
        ranked = sorted(by_category.items(), key=lambda item: item[1], reverse=True)[
            :top
        ]
        budget = self.store.get_budget(month)
        usage = (expense / budget.amount * 100) if budget else None
        return {
            "month": month,
            "income": income,
            "expense": expense,
            "balance": income - expense,
            "top": ranked,
            "budget": budget.amount if budget else None,
            "usage": usage,
            "over_budget": bool(budget and expense > budget.amount),
            "sample_count": sample_count,
        }

    def categories(self) -> list[str]:
        return self.store.categories()

    def add_category(self, name: str) -> bool:
        name = name.strip()
        if not name:
            raise AppError(
                "카테고리명이 비어 있습니다.", "비어 있지 않은 이름을 입력하세요."
            )
        return self.store.add_category(name)

    def remove_category(self, name: str) -> bool:
        name = name.strip()
        transactions = list(self.transactions.iter_all())
        if any(tx.category == name for tx in transactions):
            raise AppError(
                "사용 중인 카테고리는 삭제할 수 없습니다.",
                "거래를 다른 카테고리로 수정한 뒤 삭제하세요.",
            )
        return self.store.remove_category(name)

    def update_transaction(self, tx_id: str, changes: dict[str, object]) -> bool:
        if not changes:
            raise AppError(
                "수정할 값이 없습니다.", "예: update --id TX-000001 --amount 20000"
            )

        def updater(tx: Transaction) -> Transaction:
            values = {}
            if "date" in changes and changes["date"] is not None:
                values["date"] = validate_date(str(changes["date"]))
            if "type" in changes and changes["type"] is not None:
                values["type"] = validate_type(str(changes["type"]))
            if "category" in changes and changes["category"] is not None:
                values["category"] = self.require_category(str(changes["category"]))
            if "amount" in changes and changes["amount"] is not None:
                values["amount"] = validate_amount(changes["amount"])
            if "memo" in changes and changes["memo"] is not None:
                values["memo"] = str(changes["memo"])
            if "tags" in changes and changes["tags"] is not None:
                values["tags"] = parse_tags(str(changes["tags"]))
            return replace(tx, **values)

        return self.transactions.update(tx_id, updater)

    def delete_transaction(self, tx_id: str) -> bool:
        return self.transactions.delete(tx_id)

    def import_csv(self, source: Path) -> tuple[int, int]:
        return csv_io.import_csv(self, source)

    def export_csv(
        self,
        target: Path,
        month: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> int:
        return csv_io.export_csv(self, target, month, date_from, date_to)

    def backup(self) -> Path:
        return self.store.backup()

    def add_recurring(
        self,
        tx_type: str,
        day: str | int,
        amount: str | int,
        category: str,
        memo: str = "",
        tags: str | None = None,
    ) -> RecurringRule:
        return recurring.add_recurring(self, tx_type, day, amount, category, memo, tags)

    def apply_recurring(self, month: str) -> int:
        return recurring.apply_recurring(self, month)
