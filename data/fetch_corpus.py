"""Fetch a small Korean public-domain corpus from Korean Wikipedia.

Used as input to `python -m k_pii.eval.fp_collector` for collecting common
nouns that the PERSON detector currently over-matches. The articles chosen
are abstract/institutional topics (laws, administrative concepts) — they
contain proper nouns (positions, agencies) but few individual person names,
which is the FP territory we want to study.

Not part of the library. Sits under data/ so it's git-ignored except for
this small fetcher script.
"""
from __future__ import annotations

import json
import urllib.parse
import urllib.request
from pathlib import Path

TITLES = [
    "개인정보 보호법",
    "주민등록번호",
    "행정구역",
    "공문서",
    "정부조직법",
    "민원",
    "행정안전부",
    "대한민국의 행정부",
    "공무원",
    "감사원",
    "국세청",
    "행정심판",
]

USER_AGENT = "k-pii-research/0.1 (https://github.com/modak000/k-pii)"


def fetch_extract(title: str) -> str:
    encoded = urllib.parse.quote(title)
    url = (
        "https://ko.wikipedia.org/w/api.php"
        f"?action=query&format=json&titles={encoded}"
        "&prop=extracts&explaintext=1&exsectionformat=plain&redirects=1"
    )
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    pages = data["query"]["pages"]
    page = next(iter(pages.values()))
    return page.get("extract", "")


def main() -> None:
    out_dir = Path(__file__).parent / "corpus"
    out_dir.mkdir(parents=True, exist_ok=True)
    combined_path = out_dir / "wiki_corpus.txt"
    parts = []
    for title in TITLES:
        try:
            text = fetch_extract(title)
        except Exception as e:
            print(f"  skip {title}: {e}")
            continue
        if not text:
            print(f"  empty {title}")
            continue
        parts.append(f"=== {title} ===\n{text}\n")
        print(f"  {title}: {len(text):,} chars")
    combined = "\n".join(parts)
    combined_path.write_text(combined, encoding="utf-8")
    print(f"\nTotal: {len(combined):,} chars → {combined_path}")


if __name__ == "__main__":
    main()
