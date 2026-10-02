"""임시 데이터 디렉토리에서 실제 가계부 CLI를 검증한다."""

import csv
import os
import subprocess
import sys

import pytest

pytestmark = pytest.mark.smoke


@pytest.fixture
def cli(tmp_path):
    data = tmp_path / "data"
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")

    def run(*args, check=True, input_text=None):
        result = subprocess.run(
            [sys.executable, "-m", "budget_app", "--data-dir", str(data), *args],
            cwd=tmp_path,
            env=env,
            input=input_text,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if check:
            assert result.returncode == 0, result.stdout + result.stderr
        return result

    return run


def test_csv_summary_export_and_backup(cli, tmp_path):
    cli("category", "list")
    cli("budget", "set", "--month", "2024-01", "--amount", "500000")
    source = tmp_path / "input.csv"
    with source.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["date", "type", "category", "amount", "memo", "tags"])
        writer.writerow(["2024-01-15", "expense", "food", "12000", "실행 검증", "검증"])
    cli("import", "--from", str(source))
    assert "실행 검증" in cli("list").stdout
    assert "12,000" in cli("summary", "--month", "2024-01").stdout
    target = tmp_path / "output.csv"
    cli("export", "--out", str(target), "--month", "2024-01")
    with target.open(encoding="utf-8-sig") as file:
        records = list(csv.DictReader(file))
    assert len(records) == 1 and records[0]["amount"] == "12000"
    cli("backup")
    assert list((tmp_path / "data/backups").glob("*/transactions.jsonl"))


def test_invalid_month_returns_nonzero(cli):
    assert cli("summary", "--month", "2024-99", check=False).returncode != 0


@pytest.mark.parametrize("limit", ["0", "-1"])
def test_search_rejects_nonpositive_limit(cli, limit):
    result = cli("search", "--limit", limit, check=False)
    assert result.returncode != 0 and "limit" in result.stderr


def test_category_deletion_keeps_recurring_rule_usable(cli):
    cli(
        "recurring",
        "add",
        "--type",
        "expense",
        "--day",
        "5",
        "--amount",
        "1000",
        "--category",
        "rent",
    )
    result = cli("category", "remove", "rent", check=False)
    assert result.returncode != 0 and "카테고리" in result.stderr
    assert "created=1" in cli("recurring", "apply", "--month", "2024-02").stdout


def test_interactive_crud_and_filtered_search(cli):
    cli("category", "add", "travel")
    cli("add", input_text="2024-01-15\nexpense\ntravel\n12000\nTrain Ticket\ntrip\n")
    assert "TX-000001" in cli("list", "--limit", "1").stdout
    assert (
        "Train Ticket"
        in cli(
            "search",
            "--from",
            "2024-01-01",
            "--to",
            "2024-01-31",
            "--category",
            "travel",
            "--type",
            "expense",
            "--q",
            "ticket",
            "--tag",
            "trip",
        ).stdout
    )
    cli("update", "--id", "TX-000001", "--amount", "20000", "--memo", "Changed")
    assert "20,000" in cli("summary", "--month", "2024-01").stdout
    assert "Changed" in cli("list").stdout
    assert cli("category", "remove", "travel", check=False).returncode != 0
    cli("delete", "--id", "TX-000001")
    assert "데이터 없음" in cli("list").stdout
    cli("category", "remove", "travel")
    assert "travel" not in cli("category", "list").stdout


@pytest.mark.parametrize(
    "option,value",
    [
        ("--date", "2024-02-30"),
        ("--type", "invalid"),
        ("--amount", "0"),
        ("--category", "unknown"),
    ],
)
def test_invalid_update_preserves_transaction(cli, tmp_path, option, value):
    cli("add", input_text="2024-01-15\nexpense\nfood\n1000\nOriginal\n\n")
    path = tmp_path / "data/transactions.jsonl"
    original = path.read_bytes()
    result = cli("update", "--id", "TX-000001", option, value, check=False)
    assert result.returncode != 0 and "[오류]" in result.stderr
    assert path.read_bytes() == original
