"""통합 Anonymizer — 검출 + 정책 결정 + 처리 (BLOCK / REVIEW / ALLOW) 의 외부 API.

    from k_pii import Anonymizer, ProcessingMode

    anon = Anonymizer(mode=ProcessingMode.STRICT)
    result = anon.process("신청인 880101-1234568 연락처 010-1234-5678")
    print(result.text)        # 치환된 본문
    print(result.detections)  # 모든 검출 결과 (Action 포함)
    print(result.summary)     # by_risk / by_action / by_legal_basis
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Optional

from k_pii.core.modes import Action, ProcessingMode, policy_for
from k_pii.core.types import DetectionResult, RiskLevel
from k_pii.detect import detect_all
from k_pii.modes._apply import apply_substitutions
from k_pii.modes.redact import label_to_hangul
from k_pii.vault.reversible import ReversibleVault


@dataclass
class DetectionRecord:
    detection: DetectionResult
    action: Action
    token: Optional[str] = None


@dataclass
class AnonymizationResult:
    text: str
    detections: list[DetectionRecord]
    vault: Optional[ReversibleVault]
    summary: dict = field(default_factory=dict)

    def review_items(self) -> list[DetectionRecord]:
        return [r for r in self.detections if r.action == Action.REVIEW]

    def blocked_items(self) -> list[DetectionRecord]:
        return [r for r in self.detections if r.action == Action.BLOCK]


class Anonymizer:
    """High-level orchestration object.

    Parameters
    ----------
    mode :
        Threshold profile. See :class:`k_pii.core.modes.ProcessingMode`.
    strategy :
        ``"tokenize"`` (reversible, default), ``"redact"`` (irreversible
        label), ``"asterisk"``, ``"hashed"``.
    vault :
        Optional pre-existing :class:`ReversibleVault`. A new one is created
        if absent (used for ``tokenize`` and ``hashed``).
    include / exclude :
        Filter detectors by label.
    """

    def __init__(
        self,
        mode: ProcessingMode = ProcessingMode.STRICT,
        strategy: str = "tokenize",
        vault: Optional[ReversibleVault] = None,
        include: Optional[Iterable[str]] = None,
        exclude: Optional[Iterable[str]] = None,
    ):
        if strategy not in {"tokenize", "redact", "asterisk", "hashed"}:
            raise ValueError(f"Unknown strategy: {strategy}")
        self.mode = mode
        self.policy = policy_for(mode)
        self.strategy = strategy
        self.vault = vault if vault is not None else ReversibleVault()
        self.include = list(include) if include else None
        self.exclude = list(exclude) if exclude else None

    # ------------------------------------------------------------ public

    def process(self, text: str) -> AnonymizationResult:
        detections = detect_all(
            text, include=self.include, exclude=self.exclude
        )
        decisions = [
            DetectionRecord(
                detection=d,
                action=self.policy.decide(d.risk_level, d.confidence),
            )
            for d in detections
        ]

        to_block = [r for r in decisions if r.action == Action.BLOCK]
        replaced = self._apply(text, to_block)
        summary = self._build_summary(decisions)
        return AnonymizationResult(
            text=replaced,
            detections=decisions,
            vault=self.vault if self.strategy in {"tokenize", "hashed"} else None,
            summary=summary,
        )

    # ----------------------------------------------------------- internal

    def _apply(self, text: str, to_block: list[DetectionRecord]) -> str:
        if not to_block:
            return text

        if self.strategy == "tokenize":
            def repl(d: DetectionResult) -> str:
                tok = self.vault.store(
                    label=d.label,
                    original=d.text,
                    risk_level=int(d.risk_level),
                    legal_basis=d.legal_basis,
                    offset=d.start,
                    extra=dict(d.extra),
                )
                # Tag the record with the token assigned.
                for rec in to_block:
                    if rec.detection is d:
                        rec.token = tok
                        break
                return tok
            return apply_substitutions(
                text, (r.detection for r in to_block), repl
            )

        if self.strategy == "redact":
            def repl(d):
                return f"[{label_to_hangul(d.label)}]"
            return apply_substitutions(
                text, (r.detection for r in to_block), repl
            )

        if self.strategy == "asterisk":
            def repl(d):
                return "*" * max(1, d.end - d.start)
            return apply_substitutions(
                text, (r.detection for r in to_block), repl
            )

        # hashed
        def repl(d: DetectionResult) -> str:
            fp = self.vault.fingerprint(d.label, d.text)
            tok = f"<{d.label}:{fp[:12]}>"
            for rec in to_block:
                if rec.detection is d:
                    rec.token = tok
                    break
            return tok
        return apply_substitutions(text, (r.detection for r in to_block), repl)

    def _build_summary(self, decisions: list[DetectionRecord]) -> dict:
        by_action: dict[str, int] = {}
        by_risk: dict[str, int] = {}
        by_label: dict[str, int] = {}
        by_legal: dict[str, int] = {}
        for r in decisions:
            by_action[r.action.value] = by_action.get(r.action.value, 0) + 1
            risk_name = RiskLevel(r.detection.risk_level).name
            by_risk[risk_name] = by_risk.get(risk_name, 0) + 1
            by_label[r.detection.label] = by_label.get(r.detection.label, 0) + 1
            lb = r.detection.legal_basis or "—"
            by_legal[lb] = by_legal.get(lb, 0) + 1
        return {
            "total": len(decisions),
            "mode": self.mode.value,
            "strategy": self.strategy,
            "by_action": by_action,
            "by_risk": by_risk,
            "by_label": by_label,
            "by_legal_basis": by_legal,
        }
