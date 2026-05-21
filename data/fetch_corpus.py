"""Fetch a Korean public-sector corpus for fp_collector input.

Phase 1 (Wikipedia bootstrap, commit e02f135):
    11 admin/law articles from ko.wikipedia.org/w/api.php — ~25K chars.

Phase 2 (this revision):
    Real public-sector text from sources reachable from a Korean residential
    network (cloud session was blocked by Anthropic's allowlist on Korean
    .go.kr domains; the local Windows session is not):
      - korea.kr 정책브리핑   — 부처 보도자료 본문 (HTML 본문 추출)
      - casenote.kr           — 판결문 검색 결과 (HTML 본문 추출)
      - ko.wikipedia.org      — 기존 추상 토픽 (변동 없음)

Not part of the library. Output goes to data/corpus/ and feeds
``python -m k_pii.eval.fp_collector``.

Polite: 1s delay between requests, browser User-Agent, single thread.
"""
from __future__ import annotations

import html as _html
import json
import re
import ssl
import time
import urllib.parse
import urllib.request
from pathlib import Path

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 k-pii-research/0.2"
)
HEADERS = {"User-Agent": UA, "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8"}
CTX = ssl.create_default_context()
TIMEOUT = 20


def _fetch(url: str) -> str:
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, context=CTX, timeout=TIMEOUT) as resp:
        return resp.read().decode("utf-8", errors="replace")


# ----------------------------------------------------------------------------
# HTML → plain text helpers (no external dep)
# ----------------------------------------------------------------------------

_SCRIPT_STYLE = re.compile(r"<(script|style)[^>]*>.*?</\1>", re.IGNORECASE | re.DOTALL)
_TAG = re.compile(r"<[^>]+>")
_WS = re.compile(r"[ \t]+")
_NL = re.compile(r"\n{3,}")


def _strip_html(html: str) -> str:
    html = _SCRIPT_STYLE.sub(" ", html)
    html = _TAG.sub(" ", html)
    html = _html.unescape(html)
    html = _WS.sub(" ", html)
    html = _NL.sub("\n\n", html)
    return html.strip()


def _extract_div(html: str, class_name: str) -> str | None:
    # Best-effort balanced extraction — finds opening div with the class
    # and returns the substring until what looks like its matching </div>.
    # Public-sector pages are simple enough that this works.
    pat = re.compile(
        r'<div[^>]*class="[^"]*\b' + re.escape(class_name) + r'\b[^"]*"[^>]*>',
        re.IGNORECASE,
    )
    m = pat.search(html)
    if not m:
        return None
    start = m.end()
    depth = 1
    i = start
    open_re = re.compile(r"<div\b", re.IGNORECASE)
    close_re = re.compile(r"</div>", re.IGNORECASE)
    while i < len(html) and depth > 0:
        op = open_re.search(html, i)
        cl = close_re.search(html, i)
        if cl is None:
            break
        if op is not None and op.start() < cl.start():
            depth += 1
            i = op.end()
        else:
            depth -= 1
            i = cl.end()
            if depth == 0:
                return html[start:cl.start()]
    return html[start:i]


# ----------------------------------------------------------------------------
# Korean Wikipedia (kept from earlier — abstract admin/law topics)
# ----------------------------------------------------------------------------

WIKI_TITLES = [
    "개인정보 보호법", "주민등록번호", "행정구역", "공문서", "정부조직법",
    "민원", "행정안전부", "대한민국의 행정부", "공무원", "감사원",
    "국세청", "행정심판",
]


def crawl_wikipedia() -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for title in WIKI_TITLES:
        encoded = urllib.parse.quote(title)
        url = (
            "https://ko.wikipedia.org/w/api.php"
            f"?action=query&format=json&titles={encoded}"
            "&prop=extracts&explaintext=1&exsectionformat=plain&redirects=1"
        )
        try:
            data = json.loads(_fetch(url))
        except Exception as e:
            print(f"  wiki skip {title}: {e}")
            continue
        page = next(iter(data["query"]["pages"].values()))
        text = page.get("extract", "")
        if text:
            out.append((f"wiki:{title}", text))
            print(f"  wiki {title}: {len(text):,} chars")
        time.sleep(0.5)
    return out


# ----------------------------------------------------------------------------
# korea.kr — 정책브리핑 (정부 보도자료, 부처 발표문 등)
# ----------------------------------------------------------------------------

def crawl_korea_kr(max_articles: int = 25) -> list[tuple[str, str]]:
    """Crawl recent press releases from 정책브리핑."""
    list_url = "https://www.korea.kr/news/policyNewsList.do"
    try:
        html = _fetch(list_url)
    except Exception as e:
        print(f"  korea.kr list FAIL: {e}")
        return []
    ids = sorted(set(re.findall(r"newsId=(\d+)", html)))
    print(f"  korea.kr: found {len(ids)} article IDs, will fetch up to {max_articles}")
    out: list[tuple[str, str]] = []
    for nid in ids[:max_articles]:
        url = f"https://www.korea.kr/news/policyNewsView.do?newsId={nid}"
        try:
            page = _fetch(url)
        except Exception as e:
            print(f"  korea.kr {nid} FAIL: {e}")
            time.sleep(1.0)
            continue
        body_html = _extract_div(page, "article_body")
        if not body_html:
            print(f"  korea.kr {nid}: no article_body")
            time.sleep(1.0)
            continue
        text = _strip_html(body_html)
        if len(text) < 200:
            print(f"  korea.kr {nid}: too short ({len(text)})")
            time.sleep(1.0)
            continue
        out.append((f"korea.kr:{nid}", text))
        print(f"  korea.kr {nid}: {len(text):,} chars")
        time.sleep(1.0)
    return out


# ----------------------------------------------------------------------------
# casenote.kr — 판결문 검색 (민간 운영, 무료 열람 일부)
# ----------------------------------------------------------------------------

def crawl_casenote(max_cases: int = 15) -> list[tuple[str, str]]:
    """Crawl recent 판결문 from casenote.kr.

    casenote.kr publishes court rulings (already de-identified by the court).
    We search recent entries and fetch the full text of each.
    """
    # casenote search — fetch judgment listings (URL must be ASCII; Korean params encoded)
    search_url = (
        "https://casenote.kr/search/?"
        + urllib.parse.urlencode({"q": "판결", "page": "1"})
    )
    try:
        html = _fetch(search_url)
    except Exception as e:
        print(f"  casenote.kr search FAIL: {e}")
        return []
    # Case detail URLs look like /대법원/2023다12345 etc — Korean court name + case id
    case_paths = re.findall(r'href="(/[가-힣]+/[가-힣0-9]+)"', html)
    case_paths = sorted(set(case_paths))[:max_cases * 2]  # over-fetch, some may fail
    print(f"  casenote.kr: found {len(case_paths)} case paths, will fetch up to {max_cases}")
    out: list[tuple[str, str]] = []
    for path in case_paths:
        if len(out) >= max_cases:
            break
        url = "https://casenote.kr" + path
        try:
            page = _fetch(url)
        except Exception as e:
            print(f"  casenote.kr {path} FAIL: {e}")
            time.sleep(1.0)
            continue
        # casenote uses <div class="judgement"> or similar
        body_html = (
            _extract_div(page, "judgement")
            or _extract_div(page, "judgement_text")
            or _extract_div(page, "case-content")
            or _extract_div(page, "case_content")
        )
        if not body_html:
            time.sleep(1.0)
            continue
        text = _strip_html(body_html)
        if len(text) < 500:
            time.sleep(1.0)
            continue
        out.append((f"casenote:{path}", text))
        print(f"  casenote.kr {path}: {len(text):,} chars")
        time.sleep(1.0)
    return out


# ----------------------------------------------------------------------------
# law.go.kr — 국가법령정보 (법령 본문, PII 없음)
# ----------------------------------------------------------------------------

LAW_TITLES = [
    "개인정보 보호법", "행정절차법", "행정심판법", "공공기록물 관리에 관한 법률",
    "국민건강보험법", "민원 처리에 관한 법률",
]


def crawl_law_go_kr() -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for title in LAW_TITLES:
        encoded = urllib.parse.quote(title)
        # law.go.kr has a search-by-name endpoint (path must be fully ASCII)
        url = f"https://www.law.go.kr/{urllib.parse.quote('법령')}/{encoded}"
        try:
            page = _fetch(url)
        except Exception as e:
            print(f"  law.go.kr {title} FAIL: {e}")
            continue
        # law.go.kr embeds the law text in a content area
        body_html = (
            _extract_div(page, "lawcon")
            or _extract_div(page, "law_content")
            or _extract_div(page, "content")
        )
        if not body_html:
            print(f"  law.go.kr {title}: no content div found")
            continue
        text = _strip_html(body_html)
        if len(text) < 500:
            print(f"  law.go.kr {title}: too short ({len(text)})")
            continue
        out.append((f"law.go.kr:{title}", text))
        print(f"  law.go.kr {title}: {len(text):,} chars")
        time.sleep(1.0)
    return out


# ----------------------------------------------------------------------------
# Orchestrator
# ----------------------------------------------------------------------------

def main() -> None:
    out_dir = Path(__file__).parent / "corpus"
    out_dir.mkdir(parents=True, exist_ok=True)

    sources = [
        ("wikipedia.txt", crawl_wikipedia),
        ("korea_kr.txt", lambda: crawl_korea_kr(max_articles=25)),
        ("casenote.txt", lambda: crawl_casenote(max_cases=15)),
        ("law_go_kr.txt", crawl_law_go_kr),
    ]

    combined_parts: list[str] = []
    for fname, fn in sources:
        print(f"\n=== {fname} ===")
        items = fn()
        if not items:
            print(f"  (no items collected)")
            continue
        parts = [f"=== {label} ===\n{text}\n" for label, text in items]
        out_path = out_dir / fname
        out_path.write_text("\n".join(parts), encoding="utf-8")
        print(f"  → {out_path} ({sum(len(t) for _, t in items):,} chars)")
        combined_parts.extend(parts)

    combined = "\n".join(combined_parts)
    (out_dir / "public_corpus.txt").write_text(combined, encoding="utf-8")
    print(f"\nCombined corpus: {len(combined):,} chars → data/corpus/public_corpus.txt")


if __name__ == "__main__":
    main()
