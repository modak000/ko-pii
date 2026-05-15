"""DOCX (Microsoft Word OOXML) 텍스트 추출 — stdlib only.

DOCX 는 ZIP + XML 구조:
  word/document.xml — 본문
  word/header*.xml — 머리말
  word/footer*.xml — 꼬리말

``<w:t>`` 요소에 텍스트가 들어 있고 ``<w:p>`` 가 문단 경계.
"""
from __future__ import annotations

import xml.etree.ElementTree as ET
import zipfile


def _extract_from_xml(xml_bytes: bytes) -> list[str]:
    parts: list[str] = []
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError:
        return parts
    for elem in root.iter():
        local = elem.tag.split("}", 1)[-1]
        if local == "t" and elem.text:
            parts.append(elem.text)
        elif local == "tab":
            parts.append("\t")
        elif local in {"br", "p"}:
            parts.append("\n")
    return parts


def read_text(path: str) -> str:
    out: list[str] = []
    with zipfile.ZipFile(path, "r") as zf:
        # Main body
        candidates = ["word/document.xml"]
        # Headers / footers
        candidates += sorted(
            n for n in zf.namelist()
            if n.startswith("word/header") or n.startswith("word/footer")
        )
        for name in candidates:
            if name in zf.namelist():
                out.extend(_extract_from_xml(zf.read(name)))
                out.append("\n")
    return "".join(out)
