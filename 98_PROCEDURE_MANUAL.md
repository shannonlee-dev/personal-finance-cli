# 98_PROCEDURE_MANUAL

## 1. 작업 폴더 준비

1. 작업할 폴더를 만든다.

복붙 명령어:
```sh
mkdir -p "$HOME/budget-work"
cd "$HOME/budget-work"
pwd
```

예상 화면/출력:
```text
/home/<현재사용자이름>/budget-work
```

2. 제출받은 `budget_app` 폴더와 `README.md`를 이 폴더에 둔다.

복붙 명령어:
```sh
cd "$HOME/budget-work"
find . -maxdepth 2 -type f | sort
```

예상 화면/출력:
```text
./README.md
./budget_app/__main__.py
...
```

## 2. 기본 환경 확인

1. Python 버전을 확인한다.

복붙 명령어:
```sh
python3 --version
```

예상 화면/출력:
```text
Python 3.10 이상 버전이 표시됩니다.
```

2. 외부 패키지는 설치하지 않는다.

복붙 명령어:
```sh
cd "$HOME/budget-work"
python3 -m budget_app --help
```

예상 화면/출력:
```text
add, list, search, summary, budget, category, update, delete, import, export, backup, recurring 명령이 표시됩니다.
```

## 3. 데이터 폴더와 기본 카테고리

1. 빈 데이터 폴더에서 카테고리 목록을 확인한다.

복붙 명령어:
```sh
cd "$HOME/budget-work"
python3 -m budget_app --data-dir ./data category list
```

예상 화면/출력:
```text
- food
- transport
- rent
...
```

2. 저장 파일이 만들어졌는지 확인한다.

복붙 명령어:
```sh
cd "$HOME/budget-work"
find data -maxdepth 1 -type f -print | sort
```

예상 화면/출력:
```text
data/budgets.jsonl
data/categories.jsonl
data/recurring.jsonl
data/transactions.jsonl
```

3. 카테고리 파일이 비어 있으면 기본 카테고리가 자동 생성되는지 확인한다.

이 앱은 안 A를 선택했다. `categories.jsonl`이 비어 있으면 `food`, `transport`, `rent`, `salary`, `utilities`, `health`, `education`, `entertainment`, `etc` 기본 카테고리를 자동 생성한다.

복붙 명령어:
```sh
cd "$HOME/budget-work"
mkdir -p ./empty-category-data
truncate -s 0 ./empty-category-data/categories.jsonl
python3 -m budget_app --data-dir ./empty-category-data category list
wc -l ./empty-category-data/categories.jsonl
```

예상 화면/출력:
```text
- education
- entertainment
- etc
- food
- health
- rent
- salary
- transport
- utilities
9 ./empty-category-data/categories.jsonl
```

## 4. 카테고리 목록/추가/삭제

1. 현재 카테고리 목록을 확인한다.

복붙 명령어:
```sh
cd "$HOME/budget-work"
python3 -m budget_app --data-dir ./data category list
```

예상 화면/출력:
```text
- education
- entertainment
- etc
- food
- health
- rent
- salary
- transport
- utilities
```

2. 새 카테고리를 추가한다.

복붙 명령어:
```sh
cd "$HOME/budget-work"
python3 -m budget_app --data-dir ./data category add hobby
```

예상 화면/출력:
```text
[저장 완료] category=hobby
```

3. 추가된 카테고리가 목록에 표시되는지 확인한다.

복붙 명령어:
```sh
cd "$HOME/budget-work"
python3 -m budget_app --data-dir ./data category list
```

예상 화면/출력:
```text
- education
- entertainment
- etc
- food
- health
- hobby
- rent
- salary
- transport
- utilities
```

4. 사용하지 않는 카테고리는 삭제할 수 있다.

복붙 명령어:
```sh
cd "$HOME/budget-work"
python3 -m budget_app --data-dir ./data category remove hobby
```

예상 화면/출력:
```text
[삭제 완료] category=hobby
```

5. 사용 중인 카테고리 삭제 처리를 확인한다.

복붙 명령어:
```sh
cd "$HOME/budget-work"
python3 -m budget_app --data-dir ./data category add hobby
printf '2024-01-20\nexpense\nhobby\n12000\n보드게임\nfun\n' | python3 -m budget_app --data-dir ./data add
python3 -m budget_app --data-dir ./data category remove hobby
```

예상 화면/출력:
```text
[저장 완료] category=hobby
날짜(YYYY-MM-DD, 기본 <오늘날짜>): 타입(income/expense): 카테고리: education, entertainment, etc, food, health, hobby, rent, salary, transport, utilities
카테고리: 금액(양수): 메모(선택): 태그(쉼표로 구분, 없으면 엔터): [저장 완료] id=TX-000001
[오류] 사용 중인 카테고리는 삭제할 수 없습니다.
[힌트] 거래를 다른 카테고리로 수정한 뒤 삭제하세요.
```

## 5. 거래 추가와 조회

1. 거래를 대화형으로 추가한다.

복붙 명령어:
```sh
cd "$HOME/budget-work"
printf '2024-01-15\nexpense\nfood\n15000\n점심\nmeal\n' | python3 -m budget_app --data-dir ./data add
```

예상 화면/출력:
```text
[저장 완료] id=TX-000001
```

2. 거래 목록을 확인한다.

복붙 명령어:
```sh
cd "$HOME/budget-work"
python3 -m budget_app --data-dir ./data list --limit 5
```

예상 화면/출력:
```text
최신 거래부터 최대 5건이 표시됩니다.
```

3. 거래를 검색한다.

복붙 명령어:
```sh
cd "$HOME/budget-work"
python3 -m budget_app --data-dir ./data search --from 2024-01-01 --to 2024-01-31 --category food --type expense --q 점심 --tag meal
```

예상 화면/출력:
```text
조건에 맞는 거래가 최신순으로 표시됩니다.
```

## 6. 예산과 요약

1. 월 예산을 설정한다.

복붙 명령어:
```sh
cd "$HOME/budget-work"
python3 -m budget_app --data-dir ./data budget set --month 2024-01 --amount 10000
```

예상 화면/출력:
```text
[저장 완료] 2024-01 예산 10000원
```

2. 월별 요약을 확인한다.

복붙 명령어:
```sh
cd "$HOME/budget-work"
python3 -m budget_app --data-dir ./data summary --month 2024-01 --top 3
```

예상 화면/출력:
```text
총 수입, 총 지출, 잔액, 예산 사용률, 지출 TOP 3가 표시됩니다.
예산을 초과하면 [WARNING] 문구가 표시됩니다.
```

## 7. 수정과 삭제

1. 옵션 방식으로 거래를 수정한다.

복붙 명령어:
```sh
cd "$HOME/budget-work"
python3 -m budget_app --data-dir ./data update --id TX-000001 --amount 20000 --memo 저녁 --tags meal,dinner
```

예상 화면/출력:
```text
[수정 완료] id=TX-000001
```

2. 수정 결과를 목록에서 확인한다.

복붙 명령어:
```sh
cd "$HOME/budget-work"
python3 -m budget_app --data-dir ./data list --limit 3
```

예상 화면/출력:
```text
TX-000001 거래의 금액이 20000, 메모가 저녁, 태그가 meal,dinner로 표시됩니다.
```

3. 존재하는 거래 삭제 처리를 확인한다.

복붙 명령어:
```sh
cd "$HOME/budget-work"
python3 -m budget_app --data-dir ./data delete --id TX-000001
```

예상 화면/출력:
```text
[삭제 완료] id=TX-000001
```

4. 삭제 결과를 목록에서 확인한다.

복붙 명령어:
```sh
cd "$HOME/budget-work"
python3 -m budget_app --data-dir ./data list --limit 3
```

예상 화면/출력:
```text
TX-000001 거래가 더 이상 표시되지 않습니다.
```

5. 없는 거래 삭제 처리를 확인한다.

복붙 명령어:
```sh
cd "$HOME/budget-work"
python3 -m budget_app --data-dir ./data delete --id TX-999999
```

예상 화면/출력:
```text
[정보] 없는 거래입니다 id=TX-999999
```

## 8. CSV 가져오기와 내보내기

1. 가져오기 CSV를 만든다.

복붙 명령어:
```sh
cd "$HOME/budget-work"
cat > import.csv <<'CSV'
date,type,category,amount,memo,tags
2024-01-25,income,salary,3000000,월급,pay
2024-01-16,expense,transport,2500,버스,commute
CSV
```

예상 화면/출력:
```text
명령이 조용히 끝나면 정상입니다.
```

2. CSV를 가져온다.

복붙 명령어:
```sh
cd "$HOME/budget-work"
python3 -m budget_app --data-dir ./data import --from import.csv
```

예상 화면/출력:
```text
[완료] imported=2, skipped=0
```

3. CSV로 내보낸다.

복붙 명령어:
```sh
cd "$HOME/budget-work"
python3 -m budget_app --data-dir ./data export --out export.csv --month 2024-01
```

예상 화면/출력:
```text
[완료] export.csv (<건수> records)
```

## 9. 보너스 기능

1. 백업을 생성한다.

복붙 명령어:
```sh
cd "$HOME/budget-work"
python3 -m budget_app --data-dir ./data backup
```

예상 화면/출력:
```text
[완료] backup=data/backups/budget_backup_<타임스탬프>
```

2. 반복 내역을 등록하고 특정 월에 생성한다.

복붙 명령어:
```sh
cd "$HOME/budget-work"
python3 -m budget_app --data-dir ./data recurring add --type expense --day 1 --amount 700000 --category rent --memo 월세 --tags fixed
python3 -m budget_app --data-dir ./data recurring apply --month 2024-02
```

예상 화면/출력:
```text
[저장 완료] recurring=RR-000001
[완료] created=1
```

## 10. 오류 처리 확인

1. 잘못된 월 입력이 스택트레이스 없이 처리되는지 확인한다.

복붙 명령어:
```sh
cd "$HOME/budget-work"
python3 -m budget_app --data-dir ./data summary --month 2024-99
```

예상 화면/출력:
```text
[오류] 월 형식이 올바르지 않습니다.
[힌트] 예: 2024-01
```
