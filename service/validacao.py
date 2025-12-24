import argparse
import json
import statistics
import math
from collections import defaultdict
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple


def load_json(path: Path) -> Any:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def normalize_code(code: Any) -> str:
    if code is None:
        return ""
    return str(code).strip()


def aggregate_items(items: List[dict]) -> Tuple[Dict[str, dict], int]:
    """
    Returns mapping item_code -> {quantity, occurrences, flags_counts}, and total distinct count
    """
    agg: Dict[str, dict] = {}
    for it in items or []:
        code = str(it.get("code") or it.get("Code") or "").strip()
        qty = float(it.get("quantity") or it.get("Quantity") or 0)
        rec = agg.setdefault(code, {"quantity": 0.0, "occurrences": 0, "flags": defaultdict(int)})
        rec["quantity"] += qty
        rec["occurrences"] += 1
        # flags
        for flag in ("isChopp", "isReturnable", "isIsotonicWater", "isTopOfPallet"):
            if it.get(flag) or it.get(flag[0].upper() + flag[1:]):
                rec["flags"][flag] += 1

    # convert defaultdicts to normal dicts
    for v in agg.values():
        v["flags"] = dict(v["flags"])

    return agg, len(agg)


def pallet_summary(p: dict) -> dict:
    items = p.get("items", [])
    agg, distinct = aggregate_items(items)
    # aggregate flags counts across all item entries
    flags_totals = defaultdict(int)
    for it in items or []:
        for flag in ("isChopp", "isReturnable", "isIsotonicWater", "isTopOfPallet"):
            if it.get(flag) or it.get(flag[0].upper() + flag[1:]):
                flags_totals[flag] += 1

    return {
        "code": normalize_code(p.get("code") or p.get("Code")),
        "occupation": float(p.get("occupation") or p.get("Occupation") or 0.0),
        "weight": float(p.get("weight") or p.get("Weight") or 0.0),
        "isClosed": bool(p.get("isClosed") or p.get("IsClosed") or False),
        "isPalletized": bool(p.get("isPalletized") or p.get("IsPalletized") or False),
        "distinct_items_count": distinct,
        "items_aggregate": agg,
        "flags_counts": dict(flags_totals),
        "raw": p,
    }


def compare_pallets(a: dict, b: dict, tolerance: float = 0.01) -> dict:
    """Compare two pallet dicts (summaries). Returns a detailed comparison dict."""
    report = {
        "code": a.get("code") or b.get("code"),
        "present_in_a": bool(a),
        "present_in_b": bool(b),
        "occupation_a": a.get("occupation") if a else None,
        "occupation_b": b.get("occupation") if b else None,
        "occupation_diff": None,
        "weight_a": a.get("weight") if a else None,
        "weight_b": b.get("weight") if b else None,
        "weight_diff": None,
        "isClosed_a": a.get("isClosed") if a else None,
        "isClosed_b": b.get("isClosed") if b else None,
        "isPalletized_a": a.get("isPalletized") if a else None,
        "isPalletized_b": b.get("isPalletized") if b else None,
        "distinct_items_count_a": a.get("distinct_items_count") if a else 0,
        "distinct_items_count_b": b.get("distinct_items_count") if b else 0,
        "item_diffs": {},
        "flags_counts_a": a.get("flags_counts") if a else {},
        "flags_counts_b": b.get("flags_counts") if b else {},
    }

    if a and b:
        report["occupation_diff"] = round(a.get("occupation") - b.get("occupation"), 6)
        report["weight_diff"] = round(a.get("weight") - b.get("weight"), 6)
        # items comparison by code
        codes = set(a.get("items_aggregate", {}).keys()) | set(b.get("items_aggregate", {}).keys())
        for code in sorted(codes):
            a_item = a.get("items_aggregate", {}).get(code)
            b_item = b.get("items_aggregate", {}).get(code)
            report["item_diffs"][code] = {
                "quantity_a": a_item.get("quantity") if a_item else 0.0,
                "quantity_b": b_item.get("quantity") if b_item else 0.0,
                "diff": (a_item.get("quantity") if a_item else 0.0) - (b_item.get("quantity") if b_item else 0.0),
                "occurrences_a": a_item.get("occurrences") if a_item else 0,
                "occurrences_b": b_item.get("occurrences") if b_item else 0,
                "flags_a": a_item.get("flags") if a_item else {},
                "flags_b": b_item.get("flags") if b_item else {},
            }

    return report


def similarity_score(cmp: dict) -> float:
    """Simple heuristic similarity score (0-100)."""
    if not cmp.get("present_in_a") or not cmp.get("present_in_b"):
        return 0.0

    score = 0.0
    weight_total = 0.0

    # occupation (25)
    weight_total += 25
    occ_a = cmp.get("occupation_a", 0.0) or 0.0
    occ_b = cmp.get("occupation_b", 0.0) or 0.0
    occ_diff = abs(occ_a - occ_b)
    occ_score = max(0.0, 25 * max(0.0, 1 - (occ_diff / (abs(occ_b) + 1e-6))))
    score += occ_score

    # weight (25)
    weight_total += 25
    w_a = cmp.get("weight_a", 0.0) or 0.0
    w_b = cmp.get("weight_b", 0.0) or 0.0
    w_diff = abs(w_a - w_b)
    w_score = max(0.0, 25 * max(0.0, 1 - (w_diff / (abs(w_b) + 1e-6))))
    score += w_score

    # booleans (isClosed + isPalletized) (20)
    weight_total += 20
    booleans_ok = 0
    total_booleans = 2
    if cmp.get("isClosed_a") == cmp.get("isClosed_b"):
        booleans_ok += 1
    if cmp.get("isPalletized_a") == cmp.get("isPalletized_b"):
        booleans_ok += 1
    score += (20 * (booleans_ok / total_booleans))

    # items overlap (30)
    weight_total += 30
    a_codes = set(cmp.get("item_diffs", {}).keys())
    b_codes = set([k for k, v in cmp.get("item_diffs", {}).items() if True])
    if a_codes or b_codes:
        inter = len(a_codes & b_codes)
        union = len(a_codes | b_codes)
        items_score = 30 * (inter / union if union else 1.0)
    else:
        items_score = 30.0
    score += items_score

    # final normalized 0-100
    return round((score / (weight_total or 1.0)) * 100.0, 2)


def build_report(map_pallets: List[dict], out_pallets: List[dict]) -> dict:
    a_map = {normalize_code(p.get("code") or p.get("Code")): p for p in map_pallets}
    b_map = {normalize_code(p.get("code") or p.get("Code")): p for p in out_pallets}

    codes = sorted(set(a_map.keys()) | set(b_map.keys()))

    details = {}
    scores = []
    for code in codes:
        a = pallet_summary(a_map.get(code)) if code in a_map else {}
        b = pallet_summary(b_map.get(code)) if code in b_map else {}
        cmp = compare_pallets(a, b)
        cmp["similarity_percent"] = similarity_score(cmp)
        details[code] = cmp
        if cmp["present_in_a"] and cmp["present_in_b"]:
            scores.append(cmp["similarity_percent"])

    overall = {
        "total_pallets_in_map": len(a_map),
        "total_pallets_in_output": len(b_map),
        "matched_pallets": sum(1 for c in codes if c in a_map and c in b_map),
        "only_in_map": [c for c in codes if c in a_map and c not in b_map],
        "only_in_output": [c for c in codes if c in b_map and c not in a_map],
        "average_similarity": round(sum(scores) / len(scores), 2) if scores else 0.0,
        "median_similarity": round(sorted(scores)[len(scores) // 2], 2) if scores else 0.0,
    }

    return {"generated_at": datetime.utcnow().isoformat() + "Z", "overall": overall, "details": details}


def save_reports(report: dict, out_dir: Path) -> Tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    json_path = out_dir / f"validation_report_{ts}.json"
    md_path = out_dir / f"validation_report_{ts}.md"
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2, ensure_ascii=False)
    # Enhanced markdown with charts (if matplotlib available)
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        has_mpl = True
    except Exception:
        has_mpl = False

    def gen_charts(rep: dict, out_dir: Path) -> List[Path]:
        imgs: List[Path] = []
        details = rep.get("details", {})
        sims = [v.get("similarity_percent", 0.0) for v in details.values() if v.get("present_in_a") and v.get("present_in_b")]
        if not sims:
            return imgs

        # similarity histogram
        if has_mpl:
            try:
                fig, ax = plt.subplots(figsize=(6, 3))
                ax.hist(sims, bins=10, color="#2b8cbe", edgecolor="#08519c")
                ax.set_title("Similarity distribution (matched pallets)")
                ax.set_xlabel("Similarity (%)")
                ax.set_ylabel("Count")
                p = out_dir / f"sim_hist_{ts}.png"
                fig.tight_layout()
                fig.savefig(p, dpi=150)
                plt.close(fig)
                imgs.append(p)
            except Exception:
                pass

            # top mismatches bar chart
            try:
                worst = sorted(details.items(), key=lambda kv: kv[1].get("similarity_percent", 100.0))[:15]
                codes = [k for k, v in worst]
                vals = [v.get("similarity_percent", 0.0) for k, v in worst]
                fig, ax = plt.subplots(figsize=(8, 4))
                ax.barh(range(len(vals)), vals, color="#de2d26")
                ax.set_yticks(range(len(vals)))
                ax.set_yticklabels(codes)
                ax.set_xlabel("Similarity (%)")
                ax.set_title("Top mismatches (lowest similarity)")
                p2 = out_dir / f"top_mismatches_{ts}.png"
                fig.tight_layout()
                fig.savefig(p2, dpi=150)
                plt.close(fig)
                imgs.append(p2)
            except Exception:
                pass

        return imgs

    imgs = gen_charts(report, out_dir)

    # create a polished markdown summary
    with open(md_path, "w", encoding="utf-8") as fh:
        o = report["overall"]
        fh.write("# Palletize Validation Report\n\n")
        fh.write(f"**Generated:** {report['generated_at']}  \\n+")
        fh.write(f"**Total pallets (map):** {o['total_pallets_in_map']}  \\n+")
        fh.write(f"**Total pallets (output):** {o['total_pallets_in_output']}  \\n+")
        fh.write(f"**Matched pallets:** {o['matched_pallets']}  \\n+")
        fh.write(f"**Average similarity:** **{o['average_similarity']}%**  \\n+")
        fh.write(f"**Median similarity:** {o['median_similarity']}%\n\n")

        if imgs:
            for img in imgs:
                fh.write(f"![chart]({img.as_posix()})\n\n")

        # quick table of key KPIs
        fh.write("## Key KPIs\n\n")
        fh.write("| KPI | Value |\n")
        fh.write("|---:|:---:|\n")
        fh.write(f"| Total pallets (map) | {o['total_pallets_in_map']} |\n")
        fh.write(f"| Total pallets (output) | {o['total_pallets_in_output']} |\n")
        fh.write(f"| Matched pallets | {o['matched_pallets']} |\n")
        fh.write(f"| Average similarity | {o['average_similarity']}% |\n")
        fh.write(f"| Median similarity | {o['median_similarity']}% |\n\n")

        # lists of unmatched
        if o["only_in_map"]:
            fh.write("### Pallets present only in map file\n\n")
            for c in o["only_in_map"]:
                fh.write(f"- {c}\n")
            fh.write("\n")

        if o["only_in_output"]:
            fh.write("### Pallets present only in output file\n\n")
            for c in o["only_in_output"]:
                fh.write(f"- {c}\n")
            fh.write("\n")

        # detailed per-pallet sections (summary + small table of top item diffs)
        fh.write("## Per-pallet detail\n\n")
        details = report["details"]
        # order by similarity desc for nicer presentation (best -> worst)
        sorted_codes = sorted(details.keys(), key=lambda c: details[c].get("similarity_percent", 0.0), reverse=True)
        for c in sorted_codes:
            d = details[c]
            fh.write(f"### Pallet `{c}` — Similarity: **{d.get('similarity_percent', 0.0)}%**\n\n")
            fh.write(f"- Present in map: {d.get('present_in_a')}\n")
            fh.write(f"- Present in output: {d.get('present_in_b')}\n")
            fh.write(f"- Occupation: map={d.get('occupation_a')} output={d.get('occupation_b')} diff={d.get('occupation_diff')}\n")
            fh.write(f"- Weight: map={d.get('weight_a')} output={d.get('weight_b')} diff={d.get('weight_diff')}\n")
            fh.write(f"- isClosed: map={d.get('isClosed_a')} output={d.get('isClosed_b')}\n")
            fh.write(f"- isPalletized: map={d.get('isPalletized_a')} output={d.get('isPalletized_b')}\n")
            fh.write(f"- Distinct items: map={d.get('distinct_items_count_a')} output={d.get('distinct_items_count_b')}\n\n")

            item_diffs = d.get("item_diffs", {})
            if item_diffs:
                fh.write("**Top item differences**\n\n")
                fh.write("| Item code | Map qty | Output qty | Diff |\n")
                fh.write("|---|---:|---:|---:|\n")
                # sort by absolute diff desc
                top_items = sorted(item_diffs.items(), key=lambda kv: abs(kv[1].get("diff", 0.0)), reverse=True)[:20]
                for ic, v in top_items:
                    fh.write(f"| {ic} | {v['quantity_a']} | {v['quantity_b']} | {v['diff']} |\n")
                fh.write("\n")

    return json_path, md_path


def main():
    parser = argparse.ArgumentParser(description="Compare two palletize JSONs and produce a detailed validation report.")
    parser.add_argument("map_json", nargs="?", default=r"C:\Users\BRKEY864393\OneDrive - Anheuser-Busch InBev\My Documents\projetos\ocp\ocp_score\data\AS\output\palletize_result_map_107527.json", help="Palletize map JSON file")
    parser.add_argument("output_json", nargs="?", default=r"C:\Users\BRKEY864393\OneDrive - Anheuser-Busch InBev\My Documents\projetos\ocp\ocp_score\data\AS\output.json", help="Pallets output JSON file")
    parser.add_argument("--out-dir", default="reports", help="Directory to save reports")
    args = parser.parse_args()

    map_path = Path(args.map_json)
    out_path = Path(args.output_json)

    if not map_path.exists():
        print(f"Map file not found: {map_path}")
        return
    if not out_path.exists():
        print(f"Output file not found: {out_path}")
        return

    map_data = load_json(map_path)
    out_data = load_json(out_path)

    # try to find pallets arrays inside both
    map_pallets = map_data.get("pallets") or map_data.get("Pallets") or map_data.get("palletsPayload") or []
    out_pallets = out_data.get("pallets") or out_data.get("Pallets") or []

    report = build_report(map_pallets, out_pallets)
    json_report, md_report = save_reports(report, Path(args.out_dir))

    print(f"Reports saved: {json_report} and {md_report}")


if __name__ == "__main__":
    main()
