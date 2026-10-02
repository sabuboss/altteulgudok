# 알뜰구독 — 구독료 비교 사이트

겜스고(GamsGo) 공개 API 로 상품·플랜·가격을 매주 받아 공식 요금과 비교하는 정적 사이트. 도메인 알뜰구독.kr.

## 구조
- `crawl.py`        겜스고 API 수집 → `data/catalog.json` + `data/history/날짜.json` 스냅샷
- `data/official.json`  사람이 직접 확인한 공식 요금 (출처·확인일 포함). 여기 있는 상품만 절약률을 계산한다
- `content/products/<route>.md`  상품별 가이드 글 (있으면 상품 페이지 본문으로 들어감)
- `pages/*.md`      FAQ·운영자·개인정보 고정 페이지
- `templates/`, `static/site.css`
- `build.py`        생성 스크립트 → `dist/`
- `site.json`       사이트 이름·도메인·제휴 코드·카테고리

## 로컬 미리보기
    pip install jinja2
    python crawl.py            # 가격 새로 받기 (약 1분)
    python build.py
    python -m http.server -d dist 8000

## 배포 흐름
매주 월요일 08:41 KST (또는 push·수동 실행) → GitHub Actions 가 crawl.py → data/ 커밋 → build.py → `dist` 브랜치 → Cloudflare Pages

## Cloudflare Pages 설정
- Production branch: `dist`, Build command: (비움), Build output directory: `/`
- Custom domain: 알뜰구독.kr (퓨니코드 xn--2e0bk4j72c16t.kr)
