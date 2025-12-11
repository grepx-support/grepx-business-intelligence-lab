POC Report: Superset → MongoDB (Direct Integration Not Supported)
📌 Overview

This document explains the findings of the Proof of Concept (POC) for connecting Apache Superset directly to MongoDB.
The goal was to determine whether Superset can use MongoDB as a datasource for dashboards without additional components.

🚫 Direct Integration Status
Superset → MongoDB (Direct)

❌ Not Supported

Superset requires a SQLAlchemy-compatible SQL database, but MongoDB is a NoSQL database and does not have a functional SQLAlchemy dialect.

🔍 Key Findings
1. No SQLAlchemy Driver for MongoDB

Superset relies on SQLAlchemy.

Packages like sqlalchemy-mongodb do not exist.

MongoDB cannot be queried using SQL, which Superset requires.

2. MongoDB BI Connector Is Discontinued

Attempts to install:

Local BI Connector → Not available for Ubuntu 22.04

Atlas BI Connector → Deprecated

Download links → 403 Forbidden / removed

Since the BI Connector is gone, MongoDB cannot expose SQL for Superset.

3. Superset Documentation

Official documentation lists no support for MongoDB as a datasource.
Only SQL databases (Postgres, MySQL, MariaDB, Oracle, etc.) are supported.

📌 Conclusion
Direct Superset → MongoDB connectivity is technically impossible.

This limitation applies to:

Local MongoDB

MongoDB Atlas

Any MongoDB version

✔ Recommended Workarounds
Option A — MongoDB → PostgreSQL/MySQL → Superset

Use ETL (Python script, Airflow, Dagster, etc.)

Sync MongoDB collections into SQL tables.

Pros: Easiest, stable
Cons: Not real-time

Option B — MongoDB → Trino/Presto → Superset

Use Trino’s built-in MongoDB connector.

Superset → Trino → MongoDB
Pros: Real-time queries, widely used
Cons: Requires Trino server setup

Option C — MongoDB → Apache Drill → Superset

Drill provides SQL querying for MongoDB.
Pros: Open-source
Cons: Performance depends on data size

✔ Recommendation

Use Trino for real-time dashboards
or
ETL into PostgreSQL for stable reporting dashboards.

📁 Repo Purpose

This README covers:

POC steps attempted

Why direct connectivity fails

Supported alternatives

Recommendations for moving forward
