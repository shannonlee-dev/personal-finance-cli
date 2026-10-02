"""대화형 거래 입력."""

from .models import Transaction
from .services import BudgetService
from .validators import today_string


def prompt_transaction(service: BudgetService) -> Transaction:
    tx_date = (
        input(f"날짜(YYYY-MM-DD, 기본 {today_string()}): ").strip() or today_string()
    )
    tx_type = input("타입(income/expense): ").strip()
    print("카테고리:", ", ".join(service.categories()))
    category = input("카테고리: ").strip()
    amount = input("금액(양수): ").strip()
    memo = input("메모(선택): ").strip()
    tags = input("태그(쉼표로 구분, 없으면 엔터): ").strip()
    return service.add_transaction(tx_type, tx_date, amount, category, memo, tags)
