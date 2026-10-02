# 가계부 명령과 데이터 형식

## 실행

저장소 루트에서 `uv run --frozen budget`으로 실행합니다. `--data-dir`은 하위 명령보다 먼저 지정합니다. 기본값은 현재 디렉토리의 `./data`입니다.

```bash
uv run --frozen budget --data-dir .runtime/data --help
uv run --frozen budget --data-dir .runtime/data category list
uv run --frozen budget --data-dir .runtime/data category add travel
uv run --frozen budget --data-dir .runtime/data add
uv run --frozen budget --data-dir .runtime/data list --limit 10
uv run --frozen budget --data-dir .runtime/data search --from 2024-01-01 --to 2024-01-31 --category food --type expense
uv run --frozen budget --data-dir .runtime/data budget set --month 2024-01 --amount 500000
uv run --frozen budget --data-dir .runtime/data summary --month 2024-01 --top 3
uv run --frozen budget --data-dir .runtime/data update --id TX-000001 --amount 20000 --memo "저녁 식사"
uv run --frozen budget --data-dir .runtime/data delete --id TX-000001
```

카테고리 삭제에는 `category remove 이름`을 사용합니다. 실제 거래에서 사용하는 카테고리의 삭제 규칙은 서비스에서 검증합니다.

`list`와 `search`의 `--limit`, `summary`의 `--top`은 1 이상의 정수여야 합니다. 검색은 `--q`로 메모의 대소문자 구분 없는 부분 일치, `--tag`로 태그 일치를 추가할 수 있습니다.

## CSV 형식

UTF-8 헤더가 있는 CSV를 사용합니다.

날짜와 월은 저장·출력 시 각각 `YYYY-MM-DD`, `YYYY-MM`으로 정규화합니다. `2024-1-5`, `2024-1`처럼 0이 생략된 입력도 같은 날짜·월로 처리합니다. 기존 JSONL의 이런 값은 읽을 때 정규화해 월별 합계·검색·내보내기에 포함하며, 읽기만으로 원본 파일을 다시 쓰지 않습니다. 존재하지 않는 날짜와 월은 오류로 처리합니다.

| 열 | 필수 | 형식 |
| --- | --- | --- |
| `date` | 예 | `YYYY-MM-DD` |
| `type` | 예 | `income` 또는 `expense` |
| `category` | 예 | 이미 등록된 카테고리 |
| `amount` | 예 | 양의 정수 |
| `memo` | 아니요 | 자유 텍스트 |
| `tags` | 아니요 | 쉼표로 구분한 값 |

```bash
uv run --frozen budget --data-dir .runtime/data import --from examples/transactions.csv
uv run --frozen budget --data-dir .runtime/data export --out .runtime/export.csv --month 2024-01
uv run --frozen budget --data-dir .runtime/data export --out .runtime/export.csv --from 2024-01-01 --to 2024-01-31
```

## 반복 거래와 백업

```bash
uv run --frozen budget --data-dir .runtime/data recurring add --type expense --day 5 --amount 50000 --category food --memo "정기 지출"
uv run --frozen budget --data-dir .runtime/data recurring apply --month 2024-02
uv run --frozen budget --data-dir .runtime/data backup
```

반복 거래 적용과 가져오기는 데이터를 변경합니다. 실제 사용 전에 데이터 폴더를 백업합니다. 정상 종료 코드는 0이며 잘못된 입력은 오류 메시지와 0이 아닌 종료 코드로 안내합니다.

## 파일 저장

거래·카테고리·예산·반복 규칙은 각각 JSONL 파일에 저장합니다. 수정·삭제는 임시 파일 작성 후 `os.replace`로 교체합니다. JSONL 샘플과 CSV 입력 예제는 `examples/`에 있습니다. 실행 데이터와 백업은 지정한 데이터 디렉토리에서 관리합니다.
