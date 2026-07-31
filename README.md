# 대한민국 정치·외교 실시간 브리핑

GitHub Pages + GitHub Actions 기반 자동 수집 대시보드입니다.

## 실제 연결 출처
- 대한민국 정책브리핑 보도자료 목록 (`korea.kr`)
- 대한민국 외교부 보도자료 목록 (`mofa.go.kr`)
- Google News RSS의 공식기관 도메인 제한 검색 피드(국회·대통령실·선관위·법원·외교부·국방부·통일부 등)
- 선택사항: 네이버 뉴스 검색 API
- 선택사항: OpenAI API를 통한 구조화 요약

공식기관 페이지 구조가 변경되면 HTML 수집기가 실패할 수 있으며, 실패한 출처는 `meta.failedSources`에 기록됩니다. Google News RSS는 기관 자체 RSS가 아니라 공식기관 도메인에 한정한 검색 보조 피드입니다.

## 업로드
ZIP을 풀고 폴더 안의 파일과 폴더를 저장소 루트에 그대로 업로드하세요. `.github/workflows`와 `briefing`, `tests` 폴더 구조를 유지해야 합니다.

## GitHub 설정
1. Settings → Actions → General → Workflow permissions → Read and write permissions
2. Actions 탭에서 `Update political briefing`을 수동 실행
3. Pages는 main / (root)로 유지

## Secrets(선택)
Settings → Secrets and variables → Actions에서 등록:
- `OPENAI_API_KEY`: AI 요약용
- `NAVER_CLIENT_ID`, `NAVER_CLIENT_SECRET`: 네이버 뉴스 검색 보조 수집용

키가 없어도 공식 페이지/RSS 수집, 규칙 기반 분류·요약, 중복 제거는 동작합니다.

## 실행 일정
- 매시 7분·37분: 수집(30분 주기)
- 매일 23:00 UTC = 다음 날 08:00 KST: 전날 브리핑 확정

## 수동 확인
Actions → Update political briefing → Run workflow. 성공 후 `data.json`의 `meta.mode`가 `live`, `lastSuccessfulUpdate`가 최신 시각인지 확인하세요.

## 주의
GitHub 예약 작업은 부하에 따라 지연될 수 있습니다. 공개 저장소는 장기간 활동이 없으면 예약 워크플로가 비활성화될 수 있습니다.
