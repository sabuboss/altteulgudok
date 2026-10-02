#!/usr/bin/env python3
"""data/catalog.json + data/official.json + content/ + pages/ -> dist/  (정적 사이트 생성)

사용법:  python build.py
"""
import json, re, shutil, datetime, pathlib, glob
from jinja2 import Environment, FileSystemLoader

ROOT = pathlib.Path(__file__).parent
DIST = ROOT / "dist"
TODAY = datetime.date.today()
site = json.loads((ROOT / "site.json").read_text(encoding="utf-8"))
AFF = site["affiliate"]
env = Environment(loader=FileSystemLoader(ROOT / "templates"), autoescape=False)

# ---------- 데이터 ----------
catalog = json.loads((ROOT / "data" / "catalog.json").read_text(encoding="utf-8"))
official = {}
_p = ROOT / "data" / "official.json"
if _p.exists():
    official = json.loads(_p.read_text(encoding="utf-8")).get("products", {})


def won(n):
    try:
        return f"{int(round(float(n))):,}원"
    except Exception:
        return "-"


def deep_link(route):
    return f"https://www.gamsgo.com/ko/details/{route}?promote={AFF['promote']}"


def inline(s):
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', s)
    return s


def md(text):
    """아주 작은 마크다운: 제목, 문단, 목록, 굵게, 링크, 인용 상자."""
    out, para, lst = [], [], [None]

    def flush():
        if para:
            out.append("<p>" + " ".join(para) + "</p>")
            para.clear()
        if lst[0]:
            out.append(f"</{lst[0]}>")
            lst[0] = None

    for line in text.splitlines():
        s = line.rstrip()
        if not s:
            flush()
            continue
        m = re.match(r"^(#{1,3})\s+(.*)", s)
        if m:
            flush()
            n = len(m.group(1)) + 1
            out.append(f"<h{n}>{m.group(2)}</h{n}>")
            continue
        if s.startswith("> "):
            flush()
            out.append(f'<div class="callout">{inline(s[2:])}</div>')
            continue
        if s.startswith("! "):
            flush()
            out.append(f'<div class="callout warn">{inline(s[2:])}</div>')
            continue
        m = re.match(r"^[-*]\s+(.*)", s)
        if m:
            if lst[0] != "ul":
                flush()
                out.append("<ul>")
                lst[0] = "ul"
            out.append(f"<li>{inline(m.group(1))}</li>")
            continue
        m = re.match(r"^\d+\.\s+(.*)", s)
        if m:
            if lst[0] != "ol":
                flush()
                out.append("<ol>")
                lst[0] = "ol"
            out.append(f"<li>{inline(m.group(1))}</li>")
            continue
        if lst[0]:
            out.append(f"</{lst[0]}>")
            lst[0] = None
        para.append(inline(s))
    flush()
    return "\n".join(out)


def load_front(path):
    """--- 로 둘러싼 머리말(key: value) + 본문."""
    txt = path.read_text(encoding="utf-8")
    meta = {}
    if txt.startswith("---"):
        head, _, txt = txt[3:].partition("\n---")
        for line in head.strip().splitlines():
            k, _, v = line.partition(":")
            meta[k.strip()] = v.strip()
    return meta, txt.strip()


# ---------- 상품 가공 ----------
cat_of = {}
for key, c in site["categories"].items():
    for r in c["routes"]:
        cat_of.setdefault(r, key)


def enrich(pr):
    plans = []
    for pl in pr["plans"]:
        try:
            sale = float(pl["sale_price"])
            orig = float(pl["original_price"])
            m = int(pl["month"] or 1)
        except Exception:
            continue
        label = pl.get("screen_content") or ""
        st = pl.get("seat_type") or ""
        if st and st != label:
            label = f"{label} · {st}"
        plans.append({**pl, "sale": sale, "orig": orig, "month": m, "monthly": sale / m, "label": label})
    plans.sort(key=lambda x: (x["month"], x["monthly"]))
    best = min(plans, key=lambda x: x["monthly"]) if plans else None
    of = official.get(pr["route"], {})
    o_price = of.get("monthly")
    e = {
        **pr,
        "url": f"/p/{pr['route']}/",
        "link": deep_link(pr["route"]),
        "cat": cat_of.get(pr["route"], "etc"),
        "plans": plans,
        "best": best,
        "best_monthly": best["monthly"] if best else None,
        "gg_list_monthly": (best["orig"] / best["month"]) if best else None,
        "official": of,
        "official_monthly": o_price,
        "locked": pr.get("lock_status") == 1,
        "hot": float(pr.get("hot_score") or 0),
        "display_name": of.get("name") or pr["name"],
    }
    if best and o_price:
        e["save_pct"] = round((1 - best["monthly"] / float(o_price)) * 100)
        e["save_won"] = float(o_price) - best["monthly"]
    elif best and e["gg_list_monthly"]:
        e["gg_pct"] = round((1 - best["monthly"] / e["gg_list_monthly"]) * 100)
    g = ROOT / "content" / "products" / f"{pr['route']}.md"
    if g.exists():
        meta, body = load_front(g)
        e["guide"] = md(body)
        e["guide_meta"] = meta
    return e


products = [enrich(p) for p in catalog["products"] if p.get("route")]
by_route = {p["route"]: p for p in products}
sellable = [p for p in products if p["best"]]
top = sorted(sellable, key=lambda p: -p["hot"])[:15]
fetched = catalog["fetched_at"][:10]


# ---------- 변동 기록 ----------
def load_snapshots():
    snaps = []
    for f in sorted(glob.glob(str(ROOT / "data" / "history" / "*.json"))):
        fp = pathlib.Path(f)
        snaps.append((fp.stem, json.loads(fp.read_text(encoding="utf-8"))))
    return snaps


def diff(a, b):
    """a(이전) -> b(현재) 변동 목록"""
    ev = []
    for r, cur in b.items():
        name = cur.get("name", r)
        if r not in a:
            ev.append({"t": "new", "route": r, "name": name, "txt": f"신규 상품 등록 (최저 {won(cur.get('min'))}/월)"})
            continue
        old = a[r]
        if old.get("lock") != cur.get("lock"):
            ev.append({"t": "lock" if cur.get("lock") else "unlock", "route": r, "name": name,
                       "txt": "구매 잠김" if cur.get("lock") else "구매 다시 열림"})
        om, cm = old.get("min"), cur.get("min")
        if om and cm and abs(float(om) - float(cm)) >= 1:
            d = float(cm) - float(om)
            sign = "+" if d > 0 else ""
            ev.append({"t": "up" if d > 0 else "down", "route": r, "name": name,
                       "txt": f"최저가 {won(om)} → {won(cm)}/월 ({sign}{int(d):,}원)"})
        op, cp = set(old.get("plans", [])), set(cur.get("plans", []))
        if cp - op:
            ev.append({"t": "plan", "route": r, "name": name, "txt": "플랜 추가: " + ", ".join(sorted(cp - op))})
        if op - cp:
            ev.append({"t": "plan", "route": r, "name": name, "txt": "플랜 사라짐: " + ", ".join(sorted(op - cp))})
    for r, old in a.items():
        if r not in b:
            ev.append({"t": "gone", "route": r, "name": old.get("name", r), "txt": "목록에서 사라짐"})
    for e in ev:
        e["url"] = f"/p/{e['route']}/" if e["route"] in by_route else None
    return ev


snaps = load_snapshots()
weeks = []
for i in range(len(snaps) - 1, 0, -1):
    d2, s2 = snaps[i]
    d1, s1 = snaps[i - 1]
    weeks.append({"date": d2, "prev": d1, "events": diff(s1, s2)})
weeks = weeks[:16]
latest_events = weeks[0]["events"] if weeks else []

# ---------- 렌더 ----------
if DIST.exists():
    shutil.rmtree(DIST)
DIST.mkdir()
shutil.copytree(ROOT / "static", DIST / "static")

common = dict(site=site, aff=AFF, won=won, fetched=fetched, today=TODAY.isoformat(),
              cats=site["categories"], year=TODAY.year)
urls = []


def render(tpl, path, **kw):
    html = env.get_template(tpl).render(**common, **kw)
    if path == "/404.html":
        out = DIST / "404.html"
    else:
        out = DIST / path.strip("/") / "index.html"
        urls.append(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")


render("home.html", "/", top=top, products=sellable, events=latest_events[:8],
       title=f"{site['name']} — {site['tagline']}", desc=site["description"], nav="home")

for key, c in site["categories"].items():
    ps = sorted([p for p in sellable if p["cat"] == key], key=lambda p: -p["hot"])
    render("category.html", f"/c/{key}/", cat=c, key=key, products=ps,
           title=f"{c['name']} 구독 가격 비교 — {site['name']}",
           desc=f"{c['name']} 구독 서비스 {len(ps)}개의 공유 플랫폼 가격을 공식 요금과 비교합니다. {fetched} 확인.", nav=key)

etc = sorted([p for p in sellable if p["cat"] == "etc"], key=lambda p: -p["hot"])
render("category.html", "/c/etc/", cat={"name": "그 밖의 상품"}, key="etc", products=etc,
       title=f"그 밖의 상품 — {site['name']}", desc="분류 밖의 상품 목록.", nav="etc")

for p in products:
    if p["best"]:
        d = f"{p['display_name']} 최저 월 {won(p['best_monthly'])}"
    else:
        d = f"{p['display_name']} 현재 구매 불가"
    render("product.html", p["url"], p=p,
           title=f"{p['display_name']} 구독 가격 비교 {TODAY.year} — 공식 요금 vs 공유 플랫폼 | {site['name']}",
           desc=f"{d}. 플랜별 가격과 주의사항을 {fetched} 기준으로 정리했습니다.", nav=p["cat"])

render("changes.html", "/changes/", weeks=weeks, title=f"이번 주 바뀐 것 — {site['name']}",
       desc="구독 서비스 공유 플랫폼의 가격 변동, 신규 상품, 구매 잠김을 매주 기록합니다.", nav="changes")

for f in sorted((ROOT / "pages").glob("*.md")):
    meta, body = load_front(f)
    render("page.html", f"/{f.stem}/", body=md(body), meta=meta,
           title=f"{meta.get('title', f.stem)} — {site['name']}", desc=meta.get("description", ""), nav=f.stem)

render("404.html", "/404.html", title="페이지를 찾을 수 없습니다", desc="", nav="")

# sitemap / robots
L = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for u in urls:
    L.append(f"  <url><loc>{site['url']}{u}</loc><lastmod>{fetched}</lastmod></url>")
L.append("</urlset>")
(DIST / "sitemap.xml").write_text("\n".join(L) + "\n", encoding="utf-8")
(DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {site['url']}/sitemap.xml\n", encoding="utf-8")
(DIST / ".nojekyll").write_text("", encoding="utf-8")
print(f"built {len(urls)} pages, {len(products)} products ({len(sellable)} sellable), {len(weeks)} change weeks -> dist/")
