"""거래 저장·수정·삭제의 저장소 인터페이스."""

from __future__ import annotations

from collections.abc import Callable, Iterator

from .models import Transaction
from .storage import JsonlStore


class TransactionRepository:
    def __init__(self, store: JsonlStore) -> None:
        self.store = store

    def add(self, tx: Transaction) -> None:
        self.store.add_transaction(tx)

    def iter_all(self) -> Iterator[Transaction]:
        yield from self.store.iter_transactions()

    def update(self, tx_id: str, updater: Callable[[Transaction], Transaction]) -> bool:
        changed = False

        def rows() -> Iterator[Transaction]:
            nonlocal changed
            for tx in self.store.iter_transactions():
                if tx.id == tx_id:
                    changed = True
                    yield updater(tx)
                else:
                    yield tx

        buffered = list(rows())
        if changed:
            self.store.rewrite_transactions(buffered)
        return changed

    def delete(self, tx_id: str) -> bool:
        changed = False

        def rows() -> Iterator[Transaction]:
            nonlocal changed
            for tx in self.store.iter_transactions():
                if tx.id == tx_id:
                    changed = True
                    continue
                yield tx

        buffered = list(rows())
        if changed:
            self.store.rewrite_transactions(buffered)
        return changed
