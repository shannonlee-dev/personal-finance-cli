# Personal Finance CLI Submission

Python standard-library CLI for managing local financial records. The app stores transactions, categories, budgets, and recurring rules in JSONL files and supports CSV import/export for reviewable data exchange.

## Run

```bash
python3 -m budget_app --help
```

The default data directory is `./data`. Use `--data-dir` to isolate a scenario:

```bash
python3 -m budget_app --data-dir ./my-data category list
```

## Storage

| File | Purpose |
| --- | --- |
| `data/transactions.jsonl` | Transaction records |
| `data/categories.jsonl` | Categories |
| `data/budgets.jsonl` | Monthly budgets |
| `data/recurring.jsonl` | Recurring rules |

Missing files are created automatically. Empty category files are initialized with default categories.

## Commands

```bash
python3 -m budget_app add
python3 -m budget_app list --limit 10
python3 -m budget_app search --from 2024-01-01 --to 2024-01-31 --category food --type expense
python3 -m budget_app budget set --month 2024-01 --amount 500000
python3 -m budget_app summary --month 2024-01 --top 3
python3 -m budget_app update --id TX-000001 --amount 20000 --memo "dinner"
python3 -m budget_app delete --id TX-000001
```

## CSV

CSV files use UTF-8 with headers.

| Column | Required | Notes |
| --- | --- | --- |
| `date` | Y | `YYYY-MM-DD` |
| `type` | Y | `income` or `expense` |
| `category` | Y | Existing category |
| `amount` | Y | Positive integer |
| `memo` | N | Free text |
| `tags` | N | Comma-separated values |

```bash
python3 -m budget_app import --from import.csv
python3 -m budget_app export --out export.csv --month 2024-01
python3 -m budget_app export --out export.csv --from 2024-01-01 --to 2024-01-31
```

## Reliability Notes

- Invalid dates, non-positive amounts, unknown categories, and invalid transaction types return clear errors.
- Normal completion exits with `0`; validation failures exit non-zero.
- `update` and `delete` replace files atomically with `os.replace`.
- Search and listing read JSONL files as streams to avoid unnecessary memory growth.
