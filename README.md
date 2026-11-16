# ProductProject1 📈

**Intelligent product analytics workspace for a simulated marketplace.**

> Portfolio MVP: product KPIs, conversion funnel, exact-day cohort retention, user-level A/B testing and SRM quality check. All datasets are **synthetic**. AI assistant is a **planned feature**, not implemented in this version.

## Business context

A marketplace product team wants to understand where buyers drop off, whether new users come back, and whether a new checkout experience improves purchasing. The MVP connects exploratory dashboards with a statistically explicit experiment summary.

## Stack

Python · Pandas · NumPy · SciPy · DuckDB SQL · Streamlit · Plotly · Pytest · GitHub Actions

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m src.generate_data
streamlit run app.py
```

Generating CSVs is optional: the app will create the same synthetic dataset in memory if the CSV files are absent.

## Run tests

```bash
python -m pytest -q
```

## SQL queries

From the repository root, with DuckDB installed:

```bash
duckdb -c ".read sql/funnel.sql"
duckdb -c ".read sql/retention_d7.sql"
duckdb -c ".read sql/experiment.sql"
```

Alternatively run queries through DuckDB's Python client (`duckdb.sql(open('sql/funnel.sql').read()).df()`).

## Analytical definitions

- **Purchase conversion** = users who purchased / assigned users; one observation per user.
- **Funnel** = signed up → viewed → cart → purchase, in the fixed ordering of the simulation.
- **D7 retention** = users with an `app_open` event exactly seven days after signup / users signed up in cohort.
- **Treatment effect** = treatment purchase share minus control share (percentage points).
- **Inference** = two-sided pooled-proportion z-test; unpooled 95% Wald confidence interval.
- **SRM** = chi-square test of observed assignment against intended 50/50 split.

**Caveats:** Data is simulated with an explicitly programmed treatment effect. Statistical significance is not product impact, and no conclusion about real customers is possible. SRM checks only one aspect of experiment quality. A filtered segment is not necessarily a valid causal estimand. Only complete D30 observation cohorts are simulated.

## Repo structure

```text
app.py                    Streamlit interface
src/generate_data.py      seeded simulation
src/analytics.py          KPI, retention and experiments
sql/                      readable DuckDB SQL exercises
tests/                    analysis invariants
.github/workflows/        CI test workflow
```

## Roadmap

- [x] Synthetic event log and user table
- [x] Dashboard with platform and region filters
- [x] Funnel and exact-day retention
- [x] Two-proportion A/B evaluation with SRM
- [ ] Metric tree and drill-down anomaly diagnosis
- [ ] Sequential experiment analysis, power and MDE planning
- [ ] Event instrumentation QA and data contracts
- [ ] Controlled AI copilot: NL → pre-approved analytics functions → cited evidence
- [ ] Docker, persistent DB and public hosted demo

## Portfolio statement

Built an end-to-end product analytics MVP for a synthetic marketplace with reproducible user-level experiment analysis, SQL queries, automated tests, and interactive KPI dashboards.
