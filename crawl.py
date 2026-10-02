"""겜스고 상품·플랜·가격 수집기.
api.gamsgo2.com 의 공개 엔드포인트(getSpuList, getSkuList)를 로그인 없이 호출해
data/raw/ 에 원본 JSON을, data/catalog.json 에 정리본을 저장한다.
"""
import json, time, sys, pathlib, urllib.request
from datetime import datetime, timezone, timedelta

API = "https://api.gamsgo2.com"
HDR = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36",
    "Content-Type": "application/json",
    "Origin": "https://www.gamsgo.com",
    "Referer": "https://www.gamsgo.com/",
    "Accept-Language": "ko",
}
ROOT = pathlib.Path(__file__).parent
RAW = ROOT / "data" / "raw"; RAW.mkdir(parents=True, exist_ok=True)
KST = timezone(timedelta(hours=9))

def post(path, body, retry=3):
    data = json.dumps(body).encode()
    for i in range(retry):
        try:
            req = urllib.request.Request(API + path, data=data, headers=HDR, method="POST")
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode())
        except Exception as e:
            if i == retry - 1: raise
            time.sleep(2 * (i + 1))

CATEGORIES = {1: "전부", 2: "영상", 4: "AI 툴", 3: "뮤직", 13: "충전", 5: "소프트웨어", 14: "게임", 9: "신규"}

def fetch_spus():
    """getSpuList 는 page/limit 를 무시하고 카테고리 전체를 한 번에 돌려준다.
    카테고리별로 한 번씩 호출해 상품에 카테고리 태그를 붙인다."""
    by_id = {}
    for cid, cname in CATEGORIES.items():
        res = post("/api/index/getSpuList", {"language": "ko", "show_currency": "KRW", "category_id": cid, "page": 1, "limit": 500})
        lst = (res.get("data") or {}).get("list", [])
        (RAW / f"spulist_cat{cid}.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"category {cid} {cname}: {len(lst)}", flush=True)
        for s in lst:
            if not s.get("id"): continue   # 마켓플레이스(C2C) 카드는 id=0 → 별도 처리 대상
            e = by_id.setdefault(s["id"], dict(s, categories=[]))
            if cid != 1 and cname not in e["categories"]: e["categories"].append(cname)
        time.sleep(0.5)
    return list(by_id.values())

def fetch_sku(type_id):
    res = post("/index/getSkuList", {"language": "ko", "show_currency": "KRW", "type_id": type_id})
    (RAW / f"sku_{type_id}.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    return res.get("data") or {}

def main():
    uniq = fetch_spus()
    print(f"unique spu: {len(uniq)}", flush=True)
    catalog = []
    for n, s in enumerate(uniq, 1):
        try:
            sku = fetch_sku(s["id"])
        except Exception as e:
            print(f"  !! sku {s['id']} {s.get('detail_route')}: {e}", flush=True); sku = {}
        plans = []
        for m in (sku.get("plan") or {}).get("month", []):
            for sc in m.get("screen", []):
                plans.append({
                    "month": m.get("month"), "month_id": m.get("month_id"),
                    "screen_id": sc.get("screen_id"), "screen_content": sc.get("screen_content"),
                    "seat_type": sc.get("seat_type"), "seat_number": sc.get("seat_number"),
                    "type_plan_id": sc.get("type_plan_id"),
                    "original_price": sc.get("original_price"), "sale_price": sc.get("sale_price"),
                    "average_price": sc.get("average_price"), "discount": sc.get("discount"),
                    "extra": {k: v for k, v in sc.items() if k not in ("service_data","month_content","currency_icon1","currency_icon2","currency_show_type","average_price_unit","sort","screen_sort","month","month_id","screen_id","screen_content","seat_type","seat_number","type_plan_id","original_price","sale_price","average_price","discount","screen","substitute_recharge")},
                })
        catalog.append({
            "id": s["id"], "route": s.get("detail_route"), "name": s.get("type_name"), "name_en": s.get("type_name0"),
            "min_price": s.get("min_price"), "lock_status": s.get("lock_status"), "vip_status": s.get("vip_status"),
            "rank": s.get("rank"), "hot_score": s.get("hot_score"), "categories": s.get("categories", []), "description": s.get("description"),
            "image": s.get("image"), "thumb": s.get("thumb_img"),
            "show_status": sku.get("show_status"), "plans": plans,
        })
        print(f"[{n}/{len(uniq)}] {s.get('detail_route')}: {len(plans)} plans", flush=True)
        time.sleep(0.4)
    out = {"fetched_at": datetime.now(KST).isoformat(timespec="seconds"), "count": len(catalog), "products": catalog}
    (ROOT / "data" / "catalog.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    save_snapshot(out)
    print("saved data/catalog.json")


def save_snapshot(out):
    """주간 비교용 압축 스냅샷. data/history/YYYY-MM-DD.json (같은 날 다시 돌리면 덮어쓴다)."""
    snap = {}
    for p in out["products"]:
        plans = sorted({f"{pl['month']}개월 {pl['screen_content']}" for pl in p["plans"] if pl.get("month")})
        snap[p["route"]] = {"name": p["name"], "min": p.get("min_price"), "lock": p.get("lock_status"), "plans": plans}
    hist = ROOT / "data" / "history"; hist.mkdir(exist_ok=True)
    (hist / (out["fetched_at"][:10] + ".json")).write_text(json.dumps(snap, ensure_ascii=False, indent=0), encoding="utf-8")

if __name__ == "__main__":
    main()
