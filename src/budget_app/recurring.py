"""반복 거래 규칙 등록과 월별 적용."""

from __future__ import annotations

import calendar
from typing import TYPE_CHECKING

from .models import RecurringRule
from .validators import (
    parse_tags,
    validate_amount,
    validate_day,
    validate_month,
    validate_type,
)

if TYPE_CHECKING:
    from .services import BudgetService


def add_recurring(
    service: BudgetService,
    tx_type: str,
    day: str | int,
    amount: str | int,
    category: str,
    memo: str = "",
    tags: str | None = None,
) -> RecurringRule:
    rule = RecurringRule(
        id=service.store.next_recurring_id(),
        type=validate_type(tx_type),
        day=validate_day(day),
        amount=validate_amount(amount),
        category=service.require_category(category),
        memo=memo,
        tags=parse_tags(tags),
    )
    service.store.add_recurring(rule)
    return rule


def apply_recurring(service: BudgetService, month: str) -> int:
    month = validate_month(month)
    _, last_day = calendar.monthrange(int(month[:4]), int(month[5:7]))
    created = 0
    existing_keys = {
        (tx.date, tx.type, tx.category, tx.amount, tx.memo, tuple(tx.tags))
        for tx in service.transactions.iter_all()
        if tx.date.startswith(month)
    }
    for rule in service.store.iter_recurring():
        day = min(rule.day, last_day)
        tx_date = f"{month}-{day:02d}"
        key = (
            tx_date,
            rule.type,
            rule.category,
            rule.amount,
            rule.memo,
            tuple(rule.tags),
        )
        if key in existing_keys:
            continue
        service.add_transaction(
            tx_type=rule.type,
            tx_date=tx_date,
            amount=rule.amount,
            category=rule.category,
            memo=rule.memo,
            tags=",".join(rule.tags),
        )
        created += 1
    return created
