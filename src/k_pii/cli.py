"""CLI — k-pii input.txt --mode strict --vault vault.json --strategy tokenize.

표준 입력으로 받으려면 input 자리에 ``-`` 사용. 결과는 stdout 으로 (치환된 본문),
요약/검토는 stderr 로 출력한다. Vault 저장 경로가 지정되면 Vault JSON 도 함께 기록.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Optional

from k_pii import __version__
from k_pii.anonymizer import Anonymizer
from k_pii.core.modes import ProcessingMode
from k_pii.reporting.certificate import generate_certificate
from k_pii.reporting.summary import format_summary_text
from k_pii.vault.reversible import ReversibleVault


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="k-pii",
        description="Rule-based PII detection and reversible pseudonymization "
                    "for Korean public-sector documents.",
    )
    p.add_argument("input", help="Input file path (or '-' for stdin).")
    p.add_argument(
        "-m", "--mode",
        choices=[m.value for m in ProcessingMode],
        default=ProcessingMode.STRICT.value,
        help="Processing mode (default: STRICT).",
    )
    p.add_argument(
        "-s", "--strategy",
        choices=["tokenize", "redact", "asterisk", "hashed", "partial", "fpe"],
        default="tokenize",
        help="Substitution strategy (default: tokenize).",
    )
    p.add_argument(
        "--vault",
        help="Path to read/write the vault JSON (used by tokenize/hashed).",
    )
    p.add_argument(
        "--include",
        help="Comma-separated category labels to include (others ignored).",
    )
    p.add_argument(
        "--exclude",
        help="Comma-separated category labels to exclude.",
    )
    p.add_argument(
        "-o", "--output",
        help="Output file path (default: stdout).",
    )
    p.add_argument(
        "--report",
        help="Write a processing certificate to this path.",
    )
    p.add_argument(
        "--json-summary",
        action="store_true",
        help="Print the summary as JSON to stderr instead of text.",
    )
    p.add_argument(
        "-V", "--version",
        action="version",
        version=f"k-pii {__version__}",
    )
    return p


def _read_input(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    # 확장자 기반 자동 디스패처 (HWPX/DOCX/XLSX/CSV/TXT 등)
    from k_pii.io_ import read_text
    return read_text(path)


def _write_output(path: Optional[str], text: str) -> None:
    if not path or path == "-":
        sys.stdout.write(text)
        if not text.endswith("\n"):
            sys.stdout.write("\n")
        return
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def _split_csv(value: Optional[str]) -> Optional[list[str]]:
    if not value:
        return None
    return [t.strip() for t in value.split(",") if t.strip()]


def main(argv: Optional[list[str]] = None) -> int:
    args = _build_parser().parse_args(argv)

    text = _read_input(args.input)

    vault = None
    if args.vault and os.path.exists(args.vault):
        vault = ReversibleVault.load(args.vault)

    anon = Anonymizer(
        mode=ProcessingMode(args.mode),
        strategy=args.strategy,
        vault=vault,
        include=_split_csv(args.include),
        exclude=_split_csv(args.exclude),
    )

    result = anon.process(text)
    _write_output(args.output, result.text)

    if args.vault and result.vault is not None:
        result.vault.save(args.vault)

    if args.report:
        with open(args.report, "w", encoding="utf-8") as f:
            f.write(generate_certificate(result, document_id=args.input))

    if args.json_summary:
        sys.stderr.write(json.dumps(result.summary, ensure_ascii=False, indent=2))
        sys.stderr.write("\n")
    else:
        sys.stderr.write(format_summary_text(result))
        sys.stderr.write("\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
