"""Run the literature search strategy against PubMed and save auditable outputs.

Usage:
    export NCBI_EMAIL="you@example.com"      # recommended by NCBI
    python -m src.run_search --max-records 500

Outputs (in ./outputs):
    search_counts.csv        hit count for every named query (search log)
    yearly_counts.csv/.png   publications per year for the core query
    records.csv              downloaded records for the retrieval query
    screened_records.csv     records with rule-based screening decision
    prisma_summary.json      numbers for a PRISMA-style flow diagram
"""
import argparse
import csv
import json
from collections import Counter
from datetime import datetime
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from . import config
from .pubmed_client import PubMedClient
from .screening import classify_design, screen_record


def write_csv(path: Path, rows, fieldnames):
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--max-records", type=int, default=500, help="records to download for screening")
    ap.add_argument("--out", default="outputs", help="output directory")
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(exist_ok=True)
    client = PubMedClient()
    run_date = datetime.now().strftime("%Y-%m-%d %H:%M")

    # 1. Search log: count per named query
    print("Running search log ...")
    log_rows = []
    for name, query in config.QUERIES.items():
        n = client.count(query, config.START_DATE, config.END_DATE)
        print(f"  {name}: {n}")
        log_rows.append({"query": name, "date_limit": f"{config.START_DATE}-{config.END_DATE}",
                         "hits": n, "run_at": run_date, "search_string": query})
    write_csv(out / "search_counts.csv", log_rows,
              ["query", "date_limit", "hits", "run_at", "search_string"])

    # 2. Publication trend for the core query
    print("Counting publications per year ...")
    years, counts = [], []
    for y in range(config.START_YEAR, datetime.now().year + 1):
        years.append(y)
        counts.append(client.count(config.QUERIES["Q1_core"], f"{y}/01/01", f"{y}/12/31"))
    write_csv(out / "yearly_counts.csv", [{"year": y, "count": c} for y, c in zip(years, counts)],
              ["year", "count"])
    fig, ax = plt.subplots(figsize=(7, 3.6))
    ax.bar([str(y) for y in years], counts, color="#2F5D8A")
    ax.set_title("PubMed records per year (core query Q1)")
    ax.set_xlabel("Publication year")
    ax.set_ylabel("Records")
    if years and years[-1] == datetime.now().year:
        ax.annotate("partial year", (len(years) - 1, counts[-1]), ha="center", va="bottom", fontsize=8)
    fig.tight_layout()
    fig.savefig(out / "yearly_counts.png", dpi=200)
    plt.close(fig)

    # 3. Download + screen the retrieval set
    print(f"Downloading up to {args.max_records} records for {config.RETRIEVAL_QUERY} ...")
    query = config.QUERIES[config.RETRIEVAL_QUERY]
    total_hits = client.count(query, config.START_DATE, config.END_DATE)
    pmids = list(dict.fromkeys(client.search_ids(query, args.max_records,
                                                 config.START_DATE, config.END_DATE)))
    records = client.fetch_records(pmids)
    for rec in records:
        rec["design"] = classify_design(rec["pub_types"])
        rec["decision"], rec["reason"] = screen_record(rec)
    fields = ["pmid", "year", "title", "journal", "design", "pub_types", "doi",
              "language", "decision", "reason", "abstract"]
    write_csv(out / "records.csv", records, fields)
    write_csv(out / "screened_records.csv", records, fields)

    reasons = Counter(r["reason"] for r in records if r["decision"] == "exclude")
    candidates = [r for r in records if r["decision"] == "include_candidate"]
    prisma = {
        "run_at": run_date,
        "records_matching_query_total": total_hits,
        "records_downloaded": len(records),
        "duplicates_removed": len(pmids) - len(set(pmids)),
        "excluded_by_rules": sum(reasons.values()),
        "exclusion_reasons": dict(reasons),
        "include_candidates_for_manual_review": len(candidates),
        "candidates_by_design": dict(Counter(r["design"] for r in candidates)),
    }
    (out / "prisma_summary.json").write_text(json.dumps(prisma, indent=2), encoding="utf-8")
    print(json.dumps(prisma, indent=2))
    print(f"Done. Files written to {out.resolve()}")


if __name__ == "__main__":
    main()
