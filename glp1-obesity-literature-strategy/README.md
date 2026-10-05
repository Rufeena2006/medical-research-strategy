# glp1-obesity-literature-strategy

**Week 1 Task: Research Planning and Strategy Development (Medical Writing Internship)**

A reproducible, code-driven research plan for a contemporary medical topic:
*GLP-1 receptor agonists and dual incretin agonists for obesity: efficacy, cardiometabolic outcomes, safety and durability of effect.*

The repository runs the planned PubMed search strategy (public NCBI E-utilities, no proprietary resources),
logs every query, applies rule-based first-pass screening, and regenerates the Word strategy document.

## Repository contents

| Path | Purpose |
|---|---|
| `report/Week1_Research_Strategy_GLP1_Obesity.docx` | Final research strategy document (topic, rationale, gaps, RQs, strategy, criteria, timeline) |
| `src/config.py` | All search blocks, named queries Q1-Q7, screening vocabulary |
| `src/pubmed_client.py` | PubMed E-utilities client (esearch/efetch, rate-limited) |
| `src/screening.py` | Rule-based pre-screening and study-design classifier |
| `src/run_search.py` | Runs the searches; writes search log, yearly trend chart, screened records, PRISMA numbers |
| `src/generate_report.py` | Rebuilds the .docx, inserting live results when available |
| `tests/` | Offline unit tests (no internet needed) |

## Quick start

```bash
git clone <your-repo-url> && cd glp1-obesity-literature-strategy
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt

pytest -q                                              # offline tests

export NCBI_EMAIL="you@example.com"                    # Windows: set NCBI_EMAIL=you@example.com
python -m src.run_search --max-records 500             # needs internet; ~1-2 minutes
python -m src.generate_report --author "Your Name"     # rebuilds the report with live counts + chart
```

Optional: set `NCBI_API_KEY` (free from NCBI) for faster requests.

## Outputs (written to `outputs/`)

- `search_counts.csv`: hit count and full string for every query (search log)
- `yearly_counts.csv` / `yearly_counts.png`: publication trend
- `records.csv` / `screened_records.csv`: downloaded records with design and screening decision
- `prisma_summary.json`: numbers for a PRISMA-style flow diagram

## Notes

- Rule-based screening only produces a *candidate list*; title/abstract and full-text decisions must be made by a human reviewer.
- Landmark trial figures in the report are preliminary and should be verified against PubMed before submission.

## License

MIT
