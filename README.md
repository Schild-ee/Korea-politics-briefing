# 대한민국 정치·외교 실시간 브리핑

GitHub Pages에서 직접 실행되는 정치·외교 브리핑 대시보드입니다.

## 저장소 구조

```text
/
├── index.html
├── data.json
├── collector.py
├── README.md
└── .github/
    └── workflows/
        └── update.yml
```

## GitHub Pages 배포

1. 저장소 `Settings`
2. `Pages`
3. Source: `Deploy from a branch`
4. Branch: `main`
5. Folder: `/(root)`

사이트 주소:

```text
https://사용자명.github.io/저장소명/
```

## 중요

현재 `data.json`은 기능 확인용 데모 데이터입니다.

`collector.py`는 실제 뉴스를 수집하지 않고 업데이트 시각만 갱신합니다. 실제 자동 수집을 위해서는 공식 RSS/API 또는 허용된 데이터 소스를 연결해야 합니다.

API 키는 HTML이나 저장소 파일에 직접 넣지 말고 GitHub Actions Secrets를 사용하세요.
