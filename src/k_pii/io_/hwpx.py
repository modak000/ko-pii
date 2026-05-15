"""HWPX (한컴오피스, KS X 6101) 텍스트 추출 — stdlib only.

HWPX 는 ZIP + XML 구조:
  META-INF/manifest.xml
  Contents/section0.xml, section1.xml ...
  Contents/header.xml

각 ``section*.xml`` 의 ``<hp:p>`` (문단) 아래 ``<hp:run><hp:t>...</hp:t></hp:run>``
요소에 본문 텍스트가 들어 있다. 표·머리말·꼬리말도 같은 구조라 ``<hp:t>`` 만
재귀적으로 모으면 본문 + 표 + 머리말 다 추출 가능.

References:
- https://tech.hancom.com/hwpxformat/
- KS X 6101 (OWPML)
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
import zipfile


_HP_T_TAG_PATTERN = re.compile(r"\{[^}]+\}t$|^t$")  # local-name = "t"


def _extract_text_from_section(xml_bytes: bytes) -> list[str]:
    parts: list[str] = []
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError:
        return parts
    # Iterate every element with local-name 't' (텍스트 노드)
    for elem in root.iter():
        local = elem.tag.split("}", 1)[-1]
        if local == "t" and elem.text:
            parts.append(elem.text)
        # 줄바꿈 표시 — <hp:lineBreak/> 또는 <hp:p> 종료
        if local in {"lineBreak", "linesegarray"}:
            parts.append("\n")
    return parts


def read_text(path: str) -> str:
    out: list[str] = []
    with zipfile.ZipFile(path, "r") as zf:
        section_names = sorted(
            n for n in zf.namelist()
            if n.startswith("Contents/section") and n.endswith(".xml")
        )
        if not section_names:
            # Some HWPX variants put sections elsewhere
            section_names = sorted(
                n for n in zf.namelist()
                if n.endswith(".xml") and "section" in n.lower()
            )
        for name in section_names:
            data = zf.read(name)
            out.extend(_extract_text_from_section(data))
            out.append("\n")  # section separator
    return "".join(out)
