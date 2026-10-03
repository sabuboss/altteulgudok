# 작업 인계

**작성** 2026-10-03 (저녁 갱신) · hostname 2610381922 (데스크탑으로 추정, 스킬 메모의 DESKTOP-P55ETAG 와 다름) · main 최신 커밋 기준 (push 완료)

**앞으로는 노트북에서만 작업한다.** 이 PC 의 클로드 memory 는 노트북으로 넘어가지 않으므로, 이 노트가 유일한 인계 수단이다. 노트북 첫 세션에서 이 파일을 읽고 아래 "배경 사실"을 memory 에 옮겨 적을 것.

## 무엇을 하고 있었나

김남균은 겜스고(GamsGo, 구독 공유 플랫폼) 어필리에이트 파트너다. 블로그로만 홍보하다 2026년 들어 수익이 급락해서, 가격을 매주 자동 수집해 공식 요금과 비교하는 사이트 **알뜰구독(https://알뜰구독.kr)** 을 하루 만에 만들어 배포했다. 겜스고 공개 API 로 상품 91개를 긁어 비교표·상품 페이지를 생성하고, 매주 월요일 GitHub Actions 가 재수집·빌드·배포한다. 구글 서치콘솔·네이버 서치어드바이저 등록과 가이드 글 14편까지 마쳤다.

## 끝낸 것

- 겜스고 어필리에이트 대시보드 전수 분석 (주문 182건, 커미션 구조, 등급, 원고료 제도) → 결론은 아래 "배경 사실"
- 수집기 `crawl.py` (api.gamsgo2.com getSpuList + getSkuList, 로그인 불필요) → `data/catalog.json`, `data/history/날짜.json`
- 생성기 `build.py` + 템플릿 + CSS → 101페이지 (홈, 분류 4, 상품 91, 변동 기록, FAQ, 운영자, 개인정보, 404, sitemap, rss, _headers)
- 공식 요금 14개 직접 확인해 `data/official.json` 에 출처·확인일과 함께 기록
- 가이드 글 14편 `content/products/*.md` (챗GPT, 유튜브, 디즈니, 스포티파이, 제미나이, 넷플릭스, 듀오링고, 캡컷, 크런치롤, 그록, Perplexity, NordVPN, 캔바, 어도비)
- GitHub `sabuboss/altteulgudok` (공개) → `.github/workflows/weekly.yml` (월 08:41 KST 크론 + push) → `dist` 브랜치 → Cloudflare Pages `altteulgudok`
- 도메인 알뜰구독.kr (가비아 구매, 퓨니코드 `xn--2e0bk4j72c16t.kr`) → 네임서버 Cloudflare 로 변경, Pages 사용자 설정 도메인 연결, HTTPS 정상
- 구글 서치콘솔: 도메인 속성, DNS TXT 소유확인, 사이트맵 제출, 홈 색인 요청
- 네이버 서치어드바이저: 메타태그 소유확인(site.json `naver_verification`), 사이트맵·RSS 제출
- Cloudflare Web Analytics 비콘(site.json `cf_beacon_token`) 삽입. 유입 경로는 Cloudflare 대시보드 → Web Analytics → 알뜰구독.kr 에서 referrer 로 확인
- 배포 전 web-launch-security 점검: 정적 사이트라 대부분 해당 없음, 보안 헤더(`_headers`)만 추가

## 하다 만 것 — 여기부터 이어서

- **첫 자동 수집 확인 (2026-10-06 월 08:41 KST)**: GitHub Actions `weekly` 가 초록인지, `data/history/2026-10-06.json` 이 커밋됐는지, 사이트 "이번 주 바뀐 것"에 내용이 생겼는지. 실패하면 `crawl.py` 의 API 응답 변화를 의심할 것.
- **검색 색인 확인 (1~2주 뒤)**: 서치콘솔 "페이지" 색인 수, 서치어드바이저 사이트맵 상태.
- 나머지 상품 가이드는 수요가 보이는 상품이 생길 때만 추가 (판매 기록 없는 70여 개는 자동 설명으로 둠).
- 김남균이 직접 겪은 사례를 유튜브·스포티파이 글에 보태기 (아직 없음).
- **네이버 블로그 기존 글에 알뜰구독 링크 넣어 유입 측정 실험**: 첫 대상은 챗GPT 글(blog.naver.com/sabuboss/224206042676). 수정 포인트는 2026-10-03 대화에서 전달했고 김남균이 블로그를 직접 고친다(클로드는 네이버 접근 불가). 이후 Web Analytics 에서 blog.naver.com referrer 유입을 확인.
- 매니저에게 사이트 오픈 알리고 전용 쿠폰·요율 상향 요청 (아직 안 함).

## 정한 것

- **사이트 이름 알뜰구독, 도메인 알뜰구독.kr 만 구매.** 영문 보조 도메인(subsave.kr 류)과 알뜰구독.com 은 트래픽 생긴 뒤 검토. 이유: 아직 선점 위험이 낮고, 한글 도메인은 카카오톡 공유에 충분.
- **"판매자"가 아니라 "검토자" 포지션.** 캡컷·캔바·넷플릭스처럼 "사지 말라"에 가까운 글을 일부러 둔다. 모든 상품을 권하면 광고로 읽히고, 환불 나면 커미션도 사라지므로 수익에도 맞다.
- **공식 요금은 사람이 확인한 것만 절약률 계산.** 확인 못 한 상품은 괄호 안에 플랫폼 표기 정가, 절약률 미표시. 겜스고 표기 정가는 부풀려진 경우가 있어(Similarweb 96% 등) 믿지 않는다.
- **공유가는 sale_price/month 로 계산.** 겜스고 카드의 min_price 는 자동갱신 할인 등이 섞여 더 낮게 보이므로 상품 페이지에 "플랫폼 카드 표시가"로 따로 표기.
- **모든 글에 GamsCare+ 기본값 "보장 미적용"(끊겨도 환불 없음)과 자동 갱신 기본 ON 을 명시.** 경쟁 사이트가 빼먹는 신뢰 포인트.
- **구글 소유확인은 Cloudflare 계정 권한 위임 대신 TXT 레코드 수동 추가.** 외부에 계정 권한 안 줌. 그 TXT 레코드는 지우면 안 됨.
- **알뜰구독에 애드센스 안 붙임.** 계정 공유 안내가 구글 게시자 정책 위반 소지가 있고, 제재가 계정 단위라 마음체크 애드센스까지 위험. 수익은 겜스고 커미션으로. (2026-10-03 김남균 동의)
- 블로그 원고료 제도(글당 5만 원)는 종료됐다고 김남균이 확인. 더 거론하지 않음.

## 아직 못 정한 것

- 플랜별 "매진" 표시: sku API 에 없고 화면에만 뜸. 필요하면 브라우저 수집으로 보완.
- 마켓플레이스(C2C, /accounts 127개)·게임 충전은 미수집. 판매 기록 0 이라 당분간 제외.
- 그록·NordVPN·어도비 원화 공식 요금 미확정 (글에서는 조건만 적음).

## 손댄 파일

- `crawl.py` — 겜스고 API 수집기. 카테고리·페이지 파라미터는 API 가 무시함(항상 91개).
- `build.py` — 정적 생성기. 변동 기록은 `data/history/` 스냅샷 쌍 비교. RSS 는 가이드 글 + 주간 변동.
- `site.json` — 이름·도메인·제휴 코드(promote RbD8C, 프로모션 코드 ENDD6)·카테고리·인증 메타.
- `data/official.json` — 공식 요금 14개 (출처·확인일).
- `data/catalog.json`, `data/history/2026-10-03.json` — 첫 수집본.
- `content/products/*.md` — 가이드 14편. `---` 머리말의 `updated` 가 RSS 날짜.
- `templates/`, `static/site.css`, `pages/*.md`, `.github/workflows/weekly.yml`, `README.md`
- (저장소 밖) `../maumcheck/.claude/launch.json` — 이 PC 전용 미리보기 설정. 노트북에서는 `python -m http.server -d dist 8010` 으로 직접.

## 배경 사실 (memory 에 옮겨 적을 것)

- 겜스고 **독점 협업 파트너**: 첫구매 22%(Lv2) / 추가구매 20% / 갱신 20%. 공개 도움말의 10%/5% 보다 훨씬 높음. 특별 요율: Perplexity 12개월 50%, Edimakor·UPDF 45%, Figma 40%, Grok·Grammarly·Office365·Autodesk 35%. Cursor·Kling 0%.
- 등급 Lv2, 90일 적격 첫구매 4건, L3(24%)까지 12건 더. 환불 시 커미션 차감됨.
- 누적 주문 195건·커미션 약 126만 원·출금 약 186만 원(원고료 포함). Spotify·YouTube·ChatGPT·Duolingo 가 커미션 79%. 12개월 플랜이 57%. 2025년 월 8~11만 → 2026년 월 1~3만 원으로 급락(블로그 중단과 일치).
- 겜스고 수요 순위(hot_score): 챗GPT > 유튜브 > 디즈니 > 스포티파이 > 넷플릭스 > 제미나이 > 캡컷 > NordVPN > 크런치롤 > 어도비. 디즈니는 수요 3위인데 판매 2건 → 가장 큰 빈자리.
- 겜스고 유튜브 홍보 시 YouTube Premium 콘텐츠 포함 금지 경고 있음.
- 기술: 겜스고 사이트는 Nuxt SSR, 기본 curl 은 Cloudflare 차단이지만 브라우저 UA + `Accept-Language: ko` 면 통과. 상품 상세 URL 에 `?promote=RbD8C` 붙이면 추천 코드 저장됨(localStorage, 서버 DB 영구).
- 크롬 확장과 내장 브라우저 모두 naver.com 접근 차단 → 네이버 작업은 김남균이 직접.
- 네이버 블로그 blog.naver.com/sabuboss 가 기존 홍보 채널.

## 이어서 하려면

1. `git clone https://github.com/sabuboss/altteulgudok.git` (또는 `git pull origin main`)
2. `pip install jinja2` → `python build.py` → `python -m http.server -d dist 8010`
3. 가격 새로 받으려면 `python crawl.py` (약 1분, 로그인 불필요). 보통은 월요일 크론이 알아서 한다.
4. 첫 세션에서 이 노트의 "배경 사실"을 memory 에 저장하고, 2026-10-06 수집 결과부터 확인.
