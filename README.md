# 대한민국 정치·외교 실시간 브리핑 v2

GitHub Pages와 GitHub Actions로 운영하는 정치·외교 브리핑 대시보드입니다.

## 핵심 개선점

- 실행마다 후보·제외·중복·신규 이슈 수를 기록합니다.
- 신규 이슈가 0건이면 이유를 로그와 대시보드에 표시합니다.
- 일부 출처 실패가 전체 작업을 중단시키지 않습니다.
- 모든 출처 실패 시 기존 `data.json`을 보존합니다.
- API 키 없이 Google News RSS 검색 피드를 통해 기본 수집이 작동합니다.
- 네이버 뉴스 검색 API는 선택 기능입니다.

## 실제 기본 연결 출처

기본 활성화된 출처는 Google News RSS 검색 결과입니다.

1. 공식기관 국내정치 도메인 제한 검색
2. 공식기관 외교안보 도메인 제한 검색
3. 국내 정치 주요 보도 검색
4. 외교·안보 주요 보도 검색

정책브리핑과 외교부 직접 목록 페이지는 이전 GitHub Actions 실행에서 연결 시간 초과가 반복되어 기본 수집 대상에서 제외했습니다. 직접 사이트를 우회하거나 차단을 회피하지 않습니다.

Google News RSS는 각 공식기관 자체 RSS가 아니라 검색·발견 계층입니다. 출처 카드에는 피드가 제공한 원 게시자와 링크를 표시합니다.

## 선택 기능: 네이버 뉴스 검색 API

공식 네이버 뉴스 검색 API를 사용하려면 아래 Secrets를 등록합니다.

- `NAVER_CLIENT_ID`
- `NAVER_CLIENT_SECRET`

등록 위치:

`Settings → Secrets and variables → Actions → New repository secret`

API 키가 없어도 기본 RSS 경로는 작동합니다.

## GitHub 업로드

ZIP 압축을 풀고 폴더 안의 모든 파일과 폴더를 저장소 최상위에 업로드합니다.

```text
/
├── index.html
├── data.json
├── collector.py
├── daily_finalize.py
├── requirements.txt
├── README.md
├── briefing/
├── tests/
└── .github/workflows/
```

기존 저장소를 완전히 교체하는 경우 이전 파일을 삭제한 뒤 새 파일을 업로드하는 편이 안전합니다. `.github`, `briefing`, `tests` 폴더 구조를 유지해야 합니다.

## GitHub Pages

1. `Settings`
2. `Pages`
3. Source: `Deploy from a branch`
4. Branch: `main`
5. Folder: `/(root)`

## Actions 쓰기 권한

1. `Settings`
2. `Actions`
3. `General`
4. `Workflow permissions`
5. `Read and write permissions`
6. `Save`

## 수동 실행

1. 저장소 상단 `Actions`
2. 왼쪽 `Update political briefing`
3. `Run workflow`
4. Branch `main`
5. 초록색 `Run workflow`

## 정상 작동 판단

Actions 실행에서 `Update briefing data`를 펼치면 아래 항목이 표시됩니다.

```text
Fetched candidates
Rejected by date
Rejected by relevance
Rejected as commentary
Duplicates
Accepted
New issues
Updated issues
Saved
```

`New issues: 0`이어도 실패라는 뜻은 아닙니다. 바로 아래 `Reason`에서 중복·기간 초과·관련성 부족·공방 제외 수를 확인합니다.

정상 실행 후 `data.json`에서 다음을 확인합니다.

- `meta.mode`: `live`
- `meta.lastSuccessfulUpdate`: 최근 실행 시각
- `meta.lastRun`: 최근 실행 진단
- `issues`: 저장된 이슈 배열

## 자동 실행

- 실시간 수집: 매시 7분, 37분
- 일일 확정: 매일 23:00 UTC, 즉 KST 오전 8시
- 화면 새 데이터 확인: 5분마다

GitHub 예약 작업은 정확한 시각보다 늦게 시작될 수 있습니다.

## 실패 출처

`data.json → meta.failedSources`와 Actions 로그에서 확인합니다.

일부 출처만 실패하면 성공한 출처 결과만 반영합니다. 모든 출처가 실패하면 기존 `data.json`을 유지합니다.

## 사이트 반영 시간

`data.json` 자동 커밋 후 GitHub Pages 재배포에는 보통 수 분이 걸릴 수 있습니다.

## 복구

잘못된 데이터가 저장되면 저장소 `Commits`에서 직전 정상 커밋으로 되돌릴 수 있습니다. 수집기가 저장하기 전 JSON 검증과 원자적 파일 교체를 수행하므로 잘못된 구조의 파일로 덮어쓰지 않습니다.
