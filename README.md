# Marketing Performance Dashboard

A Streamlit dashboard for exploring marketing campaign conversion, acquisition cost, return on investment, channel performance, and customer segments stored in PostgreSQL.

## What is implemented

- Executive campaign KPIs and campaign-level alerts
- Campaign deep dives, segment analysis, channel performance, and trends
- Read-only queries against three existing PostgreSQL reporting views or tables

The app is **not a standalone demo**: it needs a reachable PostgreSQL database with the reporting relations below. No database schema migrations, synthetic fixture, or hosted demonstration is included in this repository.

## Requirements

- Python 3.10+ and a PostgreSQL database reachable over SSL
- Read access to `marketing_gold.gold_campaign_agg`, `marketing_gold.gold_channel_agg`, and `marketing_gold.gold_segment_agg`
- Python dependencies from [requirements.txt](requirements.txt)

## Local setup

```bash
python -m venv .venv
# Activate the environment with your shell's normal command.
python -m pip install -r requirements.txt
```

Copy [the safe configuration template](.streamlit/secrets.toml.example) to `.streamlit/secrets.toml` and fill in your **own newly issued** database credentials. Do not use credentials formerly committed to this repository. The real secrets file is Git-ignored.

```bash
streamlit run app.py
```

The dashboard loads its PostgreSQL tables on startup. Errors typically mean the configured host is unreachable, SSL is unavailable, permissions are insufficient, or the expected reporting tables do not exist. The app uses SQLAlchemy's URL builder to handle special characters in database passwords.

## Security and data assumptions

- An earlier revision tracked a populated `.streamlit/secrets.toml`. **Those credentials must be rotated or revoked; deleting the file in a new commit does not erase Git history.**
- Keep real secrets in Streamlit's local ignored secrets file or in your deployment provider's secret manager.
- Only grant the application read access to its reporting tables. Do not publish database exports or customer records to this repo.
- KPI values reflect the source database; the repo does not claim live marketing outcomes or validated production figures.

## Source

[app.py](app.py) contains the Streamlit UI, SQL queries, and dashboard calculations. Contributions should include a reproducible test dataset or setup details before claiming end-to-end test coverage.
