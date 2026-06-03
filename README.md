# Personal Finance CLI

A Python command-line application for recording financial transactions, budgets, categories, recurring entries, and CSV imports/exports using local JSONL files.

The project is intentionally small and dependency-free, but it treats data handling seriously: records are validated, updates are written through temporary files, exports are reproducible, and user-facing errors avoid noisy stack traces.

## Features

- Add, list, search, update, and delete transactions
- Manage categories and monthly budgets
- Apply recurring income or expense rules
- Import and export CSV files
- Store data in JSONL files
- Create local backups
- Return clear error messages with non-zero exit codes on invalid input

## Data Files

| File | Purpose |
| --- | --- |
| `data/transactions.jsonl` | Transaction records |
| `data/categories.jsonl` | Category definitions |
| `data/budgets.jsonl` | Monthly budget limits |
| `data/recurring.jsonl` | Recurring rules |

## Run

```bash
cd submission
python3 -m budget_app --help
```

Use a separate data directory when you want isolated fixtures:

```bash
python3 -m budget_app --data-dir ./my-data category list
```

## Example Commands

```bash
python3 -m budget_app add
python3 -m budget_app list --limit 10
python3 -m budget_app search --from 2024-01-01 --to 2024-01-31 --category food
python3 -m budget_app budget set --month 2024-01 --amount 500000
python3 -m budget_app summary --month 2024-01 --top 3
```

CSV import and export:

```bash
python3 -m budget_app import --from import.csv
python3 -m budget_app export --out export.csv --month 2024-01
```

## Implementation Notes

- `Transaction`, `Budget`, and `RecurringRule` models keep the record shape explicit.
- Repository and service layers separate persistence from business rules.
- JSONL files are streamed for list and search operations.
- `update` and `delete` use temporary files followed by `os.replace`.
- Validation and CLI error handling are centralized so invalid records fail predictably.

## Repository Layout

```text
.
├── 98_PROCEDURE_MANUAL.md
├── runtime/              # captured fixtures and exports
└── submission/
    ├── budget_app/       # CLI package
    ├── data/             # sample data
    ├── my-data/          # alternate sample data
    ├── export.csv
    └── README.md
```
