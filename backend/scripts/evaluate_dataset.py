"""Comprehensive evaluation of the privacy pipeline against a gold dataset.

Measures:
1. Per-step timing  (detect / anonymize / safety-gate / full pipeline)
2. PII detection accuracy  (precision, recall, F1 with ≥50% overlap + type match)
3. Masking accuracy  (exact-match rate + token-level match, split by language)
4. Stub-LLM accuracy  (sentiment / topic on up to 50 records)

Usage (from backend/):
    uv run python scripts/evaluate_dataset.py [/path/to/dataset.jsonl]

Default dataset path: relative to repo root.
"""

from __future__ import annotations

import json
import logging
import os
import re
import statistics
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Allow running from backend/ without installing the package.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.schemas import PiiType  # noqa: E402
from app.services import anonymizer as _anonymizer  # noqa: E402
from app.services import llm_service, safety_gate  # noqa: E402
from app.services.pii_detector import PiiSpan, detect_pii  # noqa: E402

# ---------------------------------------------------------------------------
# Dataset helpers
# ---------------------------------------------------------------------------

DEFAULT_DATASET = os.path.join(
    os.path.dirname(__file__),
    "..",
    "..",
    "..",
    "fan_intelligence_gdpr_real_world_no_pattern_dataset.jsonl",
)


def load_dataset(path: str) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in Path(path).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


# Gold-type string → PiiType map  (dataset uses uppercase strings)
_GOLD_TYPE_MAP: dict[str, PiiType] = {t.value: t for t in PiiType}


# ---------------------------------------------------------------------------
# Overlap helpers
# ---------------------------------------------------------------------------


def _overlap_fraction(a_start: int, a_end: int, b_start: int, b_end: int) -> float:
    """Fraction of gold span [b_start, b_end) covered by detected span [a_start, a_end)."""
    inter = max(0, min(a_end, b_end) - max(a_start, b_start))
    gold_len = b_end - b_start
    return inter / gold_len if gold_len > 0 else 0.0


def _span_is_tp(detected: PiiSpan, gold_entity: dict[str, Any]) -> bool:
    """True if detected span overlaps ≥50% of the gold span AND types match."""
    gold_type = _GOLD_TYPE_MAP.get(gold_entity["type"])
    if gold_type is None or detected.type != gold_type:
        return False
    frac = _overlap_fraction(detected.start, detected.end, gold_entity["start"], gold_entity["end"])
    return frac >= 0.50


# ---------------------------------------------------------------------------
# Timing helpers
# ---------------------------------------------------------------------------


def _percentile(data: list[float], p: float) -> float:
    if not data:
        return 0.0
    s = sorted(data)
    idx = p / 100 * (len(s) - 1)
    lo = int(idx)
    hi = min(lo + 1, len(s) - 1)
    return s[lo] + (idx - lo) * (s[hi] - s[lo])


def _timing_stats(ms_list: list[float]) -> dict[str, float]:
    if not ms_list:
        return {}
    return {
        "min": min(ms_list),
        "mean": statistics.mean(ms_list),
        "median": statistics.median(ms_list),
        "p95": _percentile(ms_list, 95),
        "max": max(ms_list),
    }


# ---------------------------------------------------------------------------
# Token-level masking match
# ---------------------------------------------------------------------------

_TOKEN_PLACEHOLDER_RE = re.compile(r"\[[A-Z_]+_\d+\]")


def _canonical_tokens(text: str) -> list[str]:
    """Replace [TYPE_N] with [MASK] then split into word tokens (lowercased)."""
    normalised = _TOKEN_PLACEHOLDER_RE.sub("[MASK]", text).strip()
    return re.findall(r"\S+", normalised.lower())


def _token_f1(pred: str, gold: str) -> float:
    pred_toks = _canonical_tokens(pred)
    gold_toks = _canonical_tokens(gold)
    if not pred_toks and not gold_toks:
        return 1.0
    if not pred_toks or not gold_toks:
        return 0.0
    pred_c = Counter(pred_toks)
    gold_c = Counter(gold_toks)
    common = sum((pred_c & gold_c).values())
    precision = common / len(pred_toks)
    recall = common / len(gold_toks)
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


# ---------------------------------------------------------------------------
# Pretty-print helpers
# ---------------------------------------------------------------------------


def _pct(n: int, d: int) -> str:
    return f"{100.0 * n / d:5.1f}%" if d else "  n/a "


def _f(v: float) -> str:
    return f"{v:7.2f}"


def _print_timing_table(label: str, stats: dict[str, float]) -> None:
    print(
        f"  {label:<40}  "
        f"min={_f(stats['min'])}ms  "
        f"mean={_f(stats['mean'])}ms  "
        f"median={_f(stats['median'])}ms  "
        f"p95={_f(stats['p95'])}ms  "
        f"max={_f(stats['max'])}ms"
    )


# ---------------------------------------------------------------------------
# Main evaluation
# ---------------------------------------------------------------------------


def main() -> None:
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DATASET
    rows = load_dataset(path)
    n = len(rows)

    # Timing accumulators (ms)
    t_detect_ms: list[float] = []
    t_anon_ms: list[float] = []
    t_safety_ms: list[float] = []
    t_total_ms: list[float] = []

    # PII detection: per-type TP, FP, FN
    tp_by_type: Counter[str] = Counter()
    fp_by_type: Counter[str] = Counter()
    fn_by_type: Counter[str] = Counter()

    # Missed entity details (type → list of raw text snippets)
    missed_texts: dict[str, list[str]] = defaultdict(list)

    # Masking accuracy per language
    exact_by_lang: dict[str, list[bool]] = defaultdict(list)
    token_f1_by_lang: dict[str, list[float]] = defaultdict(list)

    # Stub-LLM accuracy (up to 50 records with gold labels)
    stub_results: list[dict[str, str]] = []
    stub_sample_limit = 50

    # Safety gate stats
    gate_blocked = 0

    for r in rows:
        raw: str = r["raw_message"]
        gold_entities: list[dict[str, Any]] = r.get("pii_entities", [])
        lang: str = r.get("language", "EN").upper()
        gold_masked: str = r.get("masked_message_gold", "")

        # ----------------------------------------------------------------
        # Step timings
        # ----------------------------------------------------------------
        t0 = time.perf_counter()
        spans = detect_pii(raw)
        t1 = time.perf_counter()
        result = _anonymizer.anonymize(raw, spans)
        t2 = time.perf_counter()
        gate = safety_gate.evaluate_masked(result.masked_message)
        t3 = time.perf_counter()

        t_detect_ms.append((t1 - t0) * 1000)
        t_anon_ms.append((t2 - t1) * 1000)
        t_safety_ms.append((t3 - t2) * 1000)
        t_total_ms.append((t3 - t0) * 1000)

        if not gate.safe:
            gate_blocked += 1

        # ----------------------------------------------------------------
        # PII detection accuracy  (per gold entity)
        # ----------------------------------------------------------------
        matched_gold: set[int] = set()  # indices of gold entities hit by TP

        for gi, ge in enumerate(gold_entities):
            gold_type_str = ge.get("type", "")
            hit = False
            for span in spans:
                if _span_is_tp(span, ge):
                    hit = True
                    matched_gold.add(gi)
                    break
            if hit:
                tp_by_type[gold_type_str] += 1
            else:
                fn_by_type[gold_type_str] += 1
                snippet = raw[ge["start"] : ge["end"]]
                missed_texts[gold_type_str].append(snippet)

        # False positives: detected spans that do NOT match any gold entity ≥50%
        gold_type_of_span: dict[int, str] = {}  # span index → gold type if matched
        for si, span in enumerate(spans):
            is_fp = True
            for ge in gold_entities:
                if _span_is_tp(span, ge):
                    is_fp = False
                    gold_type_of_span[si] = ge["type"]
                    break
            if is_fp:
                fp_by_type[span.type.value] += 1

        # ----------------------------------------------------------------
        # Masking accuracy
        # ----------------------------------------------------------------
        pred_masked = result.masked_message.rstrip()
        gold_masked_stripped = gold_masked.rstrip()
        exact_by_lang[lang].append(pred_masked == gold_masked_stripped)
        token_f1_by_lang[lang].append(_token_f1(pred_masked, gold_masked_stripped))

        # ----------------------------------------------------------------
        # Stub-LLM accuracy  (sample)
        # ----------------------------------------------------------------
        if (
            len(stub_results) < stub_sample_limit
            and r.get("sentiment_gold")
            and r.get("topic_key")
        ):
            try:
                input_msg = (
                    result.masked_message if gate.safe else gold_masked
                )
                analysis = llm_service.stub_analyze(input_msg)
                stub_results.append(
                    {
                        "sentiment_pred": analysis.sentiment.value,
                        "sentiment_gold": r["sentiment_gold"],
                        "topic_pred": analysis.topic.value,
                        "topic_gold": r["topic_key"],
                    }
                )
            except Exception as exc:  # noqa: BLE001
                logger.debug("Stub LLM failed for record: %s", exc)

    # ====================================================================
    # Print report
    # ====================================================================

    print()
    print("=" * 70)
    print("           PIPELINE EVALUATION REPORT")
    print("=" * 70)
    print(f"  Dataset : {path}")
    print(f"  Records : {n}")
    print()

    # ----------------------------------------------------------------
    # 1. Timing
    # ----------------------------------------------------------------
    print("─" * 70)
    print("  1. TIMING (wall-clock, ms)")
    print("─" * 70)
    _print_timing_table("detect_pii()", _timing_stats(t_detect_ms))
    _print_timing_table("anonymize()", _timing_stats(t_anon_ms))
    _print_timing_table("evaluate_masked() [safety gate]", _timing_stats(t_safety_ms))
    _print_timing_table("t_total (detect+anon+safety)", _timing_stats(t_total_ms))
    print(f"  Safety gate blocked: {gate_blocked}/{n} records ({_pct(gate_blocked, n)})")
    print()

    # ----------------------------------------------------------------
    # 2. PII detection accuracy
    # ----------------------------------------------------------------
    print("─" * 70)
    print("  2. PII DETECTION ACCURACY")
    print("─" * 70)

    all_types = sorted(set(list(tp_by_type) + list(fn_by_type) + list(fp_by_type)))
    total_tp = sum(tp_by_type.values())
    total_fp = sum(fp_by_type.values())
    total_fn = sum(fn_by_type.values())

    overall_precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) else 0.0
    overall_recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) else 0.0
    overall_f1 = (
        2 * overall_precision * overall_recall / (overall_precision + overall_recall)
        if (overall_precision + overall_recall) > 0
        else 0.0
    )

    print(
        f"  {'OVERALL':<18}  P={overall_precision:5.3f}  R={overall_recall:5.3f}  "
        f"F1={overall_f1:5.3f}   TP={total_tp}  FP={total_fp}  FN={total_fn}"
    )
    print()
    hdr = f"  {'Type':<18}  {'Prec':>6}  {'Recall':>6}  {'F1':>6}   {'TP':>4}  {'FP':>4}  {'FN':>4}"
    print(hdr)
    print(f"  {'-'*18}  {'-'*6}  {'-'*6}  {'-'*6}   {'-'*4}  {'-'*4}  {'-'*4}")
    for t in all_types:
        tp = tp_by_type[t]
        fp = fp_by_type[t]
        fn = fn_by_type[t]
        p = tp / (tp + fp) if (tp + fp) else 0.0
        r = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = 2 * p * r / (p + r) if (p + r) else 0.0
        print(f"  {t:<18}  {p:6.3f}  {r:6.3f}  {f1:6.3f}   {tp:>4}  {fp:>4}  {fn:>4}")
    print()

    # Missed entities (false negatives)
    print("  Missed entities (false negatives — up to 5 samples each):")
    any_missed = False
    for t in sorted(missed_texts):
        samples = missed_texts[t]
        any_missed = True
        shown = samples[:5]
        extra = len(samples) - len(shown)
        extra_str = f" … +{extra} more" if extra else ""
        print(f"    {t}: {len(samples)} missed — e.g. {shown}{extra_str}")
    if not any_missed:
        print("    (none — perfect recall!)")
    print()

    # ----------------------------------------------------------------
    # 3. Masking accuracy
    # ----------------------------------------------------------------
    print("─" * 70)
    print("  3. MASKING ACCURACY")
    print("─" * 70)
    print(f"  {'Lang':<6}  {'Records':>7}  {'ExactMatch':>10}  {'AvgTokenF1':>10}")
    print(f"  {'-'*6}  {'-'*7}  {'-'*10}  {'-'*10}")

    all_langs = sorted(exact_by_lang)
    for lang in all_langs:
        exacts = exact_by_lang[lang]
        f1s = token_f1_by_lang[lang]
        n_lang = len(exacts)
        exact_rate = sum(exacts) / n_lang if n_lang else 0.0
        avg_f1 = sum(f1s) / len(f1s) if f1s else 0.0
        print(f"  {lang:<6}  {n_lang:>7}  {exact_rate:>9.1%}  {avg_f1:>10.3f}")

    # Combined
    all_exacts = [v for vals in exact_by_lang.values() for v in vals]
    all_f1s = [v for vals in token_f1_by_lang.values() for v in vals]
    combined_exact = sum(all_exacts) / len(all_exacts) if all_exacts else 0.0
    combined_f1 = sum(all_f1s) / len(all_f1s) if all_f1s else 0.0
    print(f"  {'ALL':<6}  {n:>7}  {combined_exact:>9.1%}  {combined_f1:>10.3f}")
    print()

    # ----------------------------------------------------------------
    # 4. Stub LLM accuracy
    # ----------------------------------------------------------------
    print("─" * 70)
    print(f"  4. STUB LLM ACCURACY  (sample: {len(stub_results)} records)")
    print("─" * 70)
    if stub_results:
        sent_ok = sum(1 for r in stub_results if r["sentiment_pred"] == r["sentiment_gold"])
        topic_ok = sum(1 for r in stub_results if r["topic_pred"] == r["topic_gold"])
        ns = len(stub_results)
        print(f"  sentiment accuracy : {sent_ok}/{ns} = {_pct(sent_ok, ns)}")
        print(f"  topic accuracy     : {topic_ok}/{ns} = {_pct(topic_ok, ns)}")

        # Per-sentiment breakdown
        sent_breakdown: dict[str, list[bool]] = defaultdict(list)
        for r in stub_results:
            sent_breakdown[r["sentiment_gold"]].append(
                r["sentiment_pred"] == r["sentiment_gold"]
            )
        print()
        print("  Sentiment breakdown:")
        for label in sorted(sent_breakdown):
            vals = sent_breakdown[label]
            print(f"    {label:<10}: {sum(vals)}/{len(vals)} = {_pct(sum(vals), len(vals))}")

        # Per-topic breakdown
        topic_breakdown: dict[str, list[bool]] = defaultdict(list)
        for r in stub_results:
            topic_breakdown[r["topic_gold"]].append(r["topic_pred"] == r["topic_gold"])
        print()
        print("  Topic breakdown:")
        for label in sorted(topic_breakdown):
            vals = topic_breakdown[label]
            print(f"    {label:<25}: {sum(vals)}/{len(vals)} = {_pct(sum(vals), len(vals))}")
    else:
        print("  (no stub LLM results collected)")
    print()

    # ----------------------------------------------------------------
    # Summary
    # ----------------------------------------------------------------
    print("=" * 70)
    print("  SUMMARY")
    print("=" * 70)
    print(f"  Records evaluated    : {n}")
    print(f"  Mean detect latency  : {statistics.mean(t_detect_ms):.2f} ms")
    print(f"  Mean total latency   : {statistics.mean(t_total_ms):.2f} ms")
    print(
        f"  Overall PII F1       : {overall_f1:.3f}"
        f"  (P={overall_precision:.3f}, R={overall_recall:.3f})"
    )
    print(f"  Exact masking match  : {combined_exact:.1%}")
    print(f"  Token-F1 masking     : {combined_f1:.3f}")
    if stub_results:
        ns = len(stub_results)
        sent_ok = sum(1 for r in stub_results if r["sentiment_pred"] == r["sentiment_gold"])
        topic_ok = sum(1 for r in stub_results if r["topic_pred"] == r["topic_gold"])
        print(f"  Stub sentiment acc   : {_pct(sent_ok, ns)}")
        print(f"  Stub topic acc       : {_pct(topic_ok, ns)}")
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()
