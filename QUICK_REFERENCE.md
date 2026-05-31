# Quick Reference Guide: NIFTY 100 Database Design

## At-a-Glance Database Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                 NIFTY 100 STAR SCHEMA DATABASE                  │
├─────────────────────────────────────────────────────────────────┤
│ Type: Dimensional Data Warehouse (Star Schema)                  │
│ RDBMS: PostgreSQL 13+                                           │
│ Schema: nifty_100                                               │
│ Total Records: 5,474                                            │
│ Total Columns: 61                                               │
│ Estimated Size: 5-10 MB                                         │
│ Normalization: 3NF                                              │
│ Primary Pattern: Hub-and-Spoke (Companies as Hub)               │
└─────────────────────────────────────────────────────────────────┘
```

---

## Table Reference Card

### 1. COMPANIES (Dimension)

```
Purpose:        Master/Dimension table for all company data
Records:        93
Columns:        12 (see notebook for all)
Primary Key:    company_id BIGSERIAL
Foreign Keys:   None (parent table)
Main Columns:   company_name, industry, [other attributes]
Indexes:        PK, company_name (UNIQUE), industry
Size:           ~50-100 KB
Update Freq:    As needed (master data)
Query Example:  SELECT * FROM companies WHERE industry = 'Technology'
```

### 2. BALANCE_SHEET (Fact)

```
Purpose:        Financial position statements (Assets/Liabilities/Equity)
Records:        1,313
Columns:        13 (see notebook for all)
Primary Key:    balance_sheet_id BIGSERIAL
Foreign Key:    company_id → companies(company_id)
Grain:          1 row per company per reporting period
Main Columns:   company_id, reporting_date, total_assets, total_liabilities
Indexes:        PK, company_id, reporting_date, (company_id, reporting_date)
Size:           ~200-300 KB
Update Freq:    Quarterly/Annually
Query Example:  SELECT bs.*, c.company_name FROM balance_sheet bs
                JOIN companies c ON bs.company_id = c.company_id
                WHERE bs.reporting_date >= '2024-01-01'
```

### 3. PROFIT_AND_LOSS (Fact)

```
Purpose:        Income statement data (Revenue/Expenses/Profit)
Records:        1,277
Columns:        15 (see notebook for all)
Primary Key:    pl_id BIGSERIAL
Foreign Key:    company_id → companies(company_id)
Grain:          1 row per company per reporting period
Main Columns:   company_id, reporting_date, revenue, net_income
Indexes:        PK, company_id, reporting_date, (company_id, reporting_date)
Size:           ~200-300 KB
Update Freq:    Quarterly/Annually
Query Example:  SELECT company_id, reporting_date,
                (net_income / revenue * 100) as profit_margin
                FROM profit_and_loss ORDER BY profit_margin DESC
```

### 4. CASH_FLOW (Fact)

```
Purpose:        Cash movement statements (Operating/Investing/Financing)
Records:        1,188
Columns:        7 (see notebook for all)
Primary Key:    cashflow_id BIGSERIAL
Foreign Key:    company_id → companies(company_id)
Grain:          1 row per company per reporting period
Main Columns:   company_id, reporting_date, operating_cash, investing_cash, financing_cash
Indexes:        PK, company_id, reporting_date, (company_id, reporting_date)
Size:           ~150-200 KB
Update Freq:    Quarterly/Annually
Query Example:  SELECT * FROM cash_flow
                WHERE operating_cash > 0 AND reporting_date = '2024-Q3'
```

### 5. ANALYSIS (Fact)

```
Purpose:        Computed financial ratios and analysis
Records:        21 (sparse coverage ~18%)
Columns:        6+ (see notebook for all)
Primary Key:    analysis_id BIGSERIAL
Foreign Key:    company_id → companies(company_id)
Grain:          1 row per company (or per period)
Main Columns:   company_id, metric_name, metric_value
Indexes:        PK, company_id
Size:           ~5-10 KB
Update Freq:    As needed
Note:           ⚠️ Only covers ~18% of companies - verify completeness
Query Example:  SELECT c.company_name, a.metric_name, a.metric_value
                FROM companies c LEFT JOIN analysis a ON c.company_id = a.company_id
```

### 6. DOCUMENTS (Reference)

```
Purpose:        Supporting documents and files
Records:        1,586
Columns:        4 (see notebook for all)
Primary Key:    document_id BIGSERIAL
Foreign Key:    company_id → companies(company_id) ❓ TBD
Grain:          1 row per document
Main Columns:   document_name, document_type, [others]
Indexes:        PK, company_id (if FK)
Size:           ~300-400 KB
Update Freq:    As files added/updated
⚠️ PENDING:     Clarify FK relationship to companies before implementation
Query Example:  SELECT * FROM documents WHERE document_type = 'PDF'
```

### 7. PROSANDCONS (Reference)

```
Purpose:        Pros and Cons lookup/reference data
Records:        17
Columns:        4 (see notebook for all)
Primary Key:    proscons_id BIGSERIAL
Foreign Keys:   None identified
Grain:          Reference entries
Main Columns:   [See notebook]
Indexes:        PK
Size:           ~2-5 KB
Update Freq:    As needed
Query Example:  SELECT * FROM prosandcons WHERE [criteria]
```

---

## Quick SQL Templates

### Template 1: Company with Latest Financials

```sql
SELECT
    c.company_id,
    c.company_name,
    c.industry,
    bs.reporting_date,
    bs.total_assets,
    pl.revenue,
    pl.net_income,
    cf.operating_cash
FROM companies c
LEFT JOIN balance_sheet bs ON c.company_id = bs.company_id
    AND bs.reporting_date = (
        SELECT MAX(reporting_date) FROM balance_sheet
        WHERE company_id = c.company_id
    )
LEFT JOIN profit_and_loss pl ON c.company_id = pl.company_id
    AND pl.reporting_date = (
        SELECT MAX(reporting_date) FROM profit_and_loss
        WHERE company_id = c.company_id
    )
LEFT JOIN cash_flow cf ON c.company_id = cf.company_id
    AND cf.reporting_date = (
        SELECT MAX(reporting_date) FROM cash_flow
        WHERE company_id = c.company_id
    )
WHERE c.industry = 'YOUR_INDUSTRY'
ORDER BY c.company_name;
```

### Template 2: Financial Trend Analysis

```sql
SELECT
    c.company_name,
    bs.reporting_date,
    bs.total_assets,
    LAG(bs.total_assets) OVER (PARTITION BY c.company_id ORDER BY bs.reporting_date) as prev_assets,
    bs.total_assets - LAG(bs.total_assets) OVER (PARTITION BY c.company_id ORDER BY bs.reporting_date) as assets_change
FROM balance_sheet bs
JOIN companies c ON bs.company_id = c.company_id
WHERE c.company_id = YOUR_COMPANY_ID
ORDER BY bs.reporting_date;
```

### Template 3: Industry Comparison

```sql
SELECT
    c.industry,
    COUNT(DISTINCT c.company_id) as company_count,
    ROUND(AVG(pl.revenue), 2) as avg_revenue,
    ROUND(AVG(pl.net_income), 2) as avg_net_income,
    ROUND(AVG(pl.net_income / pl.revenue * 100), 2) as avg_profit_margin
FROM companies c
JOIN profit_and_loss pl ON c.company_id = pl.company_id
WHERE pl.reporting_date = (SELECT MAX(reporting_date) FROM profit_and_loss)
GROUP BY c.industry
ORDER BY avg_profit_margin DESC;
```

### Template 4: Data Quality Check

```sql
-- Check for orphaned records (FK violations)
SELECT 'balance_sheet' as table_name, COUNT(*) as orphaned_count
FROM balance_sheet bs
WHERE NOT EXISTS (SELECT 1 FROM companies c WHERE c.company_id = bs.company_id)
UNION ALL
SELECT 'profit_and_loss', COUNT(*)
FROM profit_and_loss pl
WHERE NOT EXISTS (SELECT 1 FROM companies c WHERE c.company_id = pl.company_id)
UNION ALL
SELECT 'cash_flow', COUNT(*)
FROM cash_flow cf
WHERE NOT EXISTS (SELECT 1 FROM companies c WHERE c.company_id = cf.company_id)
UNION ALL
SELECT 'analysis', COUNT(*)
FROM analysis a
WHERE NOT EXISTS (SELECT 1 FROM companies c WHERE c.company_id = a.company_id)
UNION ALL
SELECT 'documents', COUNT(*)
FROM documents d
WHERE company_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM companies c WHERE c.company_id = d.company_id);
```

---

## Key Columns Quick Reference

### Companies Table

- `company_id` (PK) - Unique identifier
- `company_name` - Company name (UNIQUE)
- `industry` - Business sector
- [12 columns total - see notebook]

### Financial Tables (BS, P&L, CF)

- `[table]_id` (PK) - Surrogate key
- `company_id` (FK) - Link to companies
- `reporting_date` - KEY for time-series analysis
- Various financial metrics (assets, revenue, cash, etc.)

### Analysis Table

- `analysis_id` (PK) - Surrogate key
- `company_id` (FK) - Link to companies
- `metric_name` - Type of ratio/metric
- `metric_value` - Calculated value

### Documents Table

- `document_id` (PK) - Surrogate key
- `company_id` (FK?) - Link to companies ❓ TBD
- `document_name` - File/doc name
- `document_type` - Classification

---

## Index Lookup Table

| Table           | Index Name                      | Columns                      | Type      | Purpose            |
| --------------- | ------------------------------- | ---------------------------- | --------- | ------------------ |
| companies       | PK                              | company_id                   | PRIMARY   | Unique ID lookup   |
| companies       | idx_name                        | company_name                 | UNIQUE    | Company lookup     |
| companies       | idx_industry                    | industry                     | REGULAR   | Industry filtering |
| balance_sheet   | PK                              | balance_sheet_id             | PRIMARY   | Record ID          |
| balance_sheet   | idx_bs_company_id               | company_id                   | REGULAR   | FK join            |
| balance_sheet   | idx_bs_date                     | reporting_date               | REGULAR   | Date range         |
| balance_sheet   | idx_bs_compound                 | (company_id, reporting_date) | COMPOSITE | Optimized joins    |
| profit_and_loss | [Same pattern as balance_sheet] |                              |           |                    |
| cash_flow       | [Same pattern as balance_sheet] |                              |           |                    |

---

## Common Issues & Solutions

### Issue 1: Slow Joins on Financial Tables

```
Symptom: Query with JOIN companies + balance_sheet is slow
Solution: Ensure indexes exist on (company_id, reporting_date)
Command: CREATE INDEX idx_bs_compound ON balance_sheet(company_id, reporting_date);
```

### Issue 2: Null Company IDs in Documents

```
Symptom: Some documents can't be linked to companies
Solution: Clarify business rule - are all documents company-linked?
Action: Update schema with NOT NULL constraint if all should be linked
```

### Issue 3: Analysis Table is Sparse

```
Symptom: Only 21 records for 93 companies (~18% coverage)
Solution: Verify if analysis is:
  a) Incomplete (missing calculations for some companies)
  b) Intentionally sparse (only certain companies analyzed)
  c) Calculated on-demand (not pre-calculated)
Recommendation: Review data quality and business logic
```

### Issue 4: Duplicate Financial Statements

```
Symptom: Multiple records for same company+date combination
Solution: Add UNIQUE constraint to (company_id, reporting_date)
Command: ALTER TABLE balance_sheet ADD CONSTRAINT uq_bs_company_date
         UNIQUE(company_id, reporting_date);
```

---

## Maintenance Commands

### Backup Strategy

```bash
# Daily backup
pg_dump -h localhost -U postgres -d nifty_100 -Fc > nifty_100_$(date +%Y%m%d).sql

# Weekly full backup with compression
pg_dump -h localhost -U postgres -d nifty_100 -Fc -v > nifty_100_full_$(date +%Y%m%d).sql.gz
```

### Consistency Checks

```sql
-- Check index health
REINDEX DATABASE nifty_100;

-- Analyze table statistics
ANALYZE;

-- Check for unused indexes
SELECT schemaname, tablename, indexname
FROM pg_indexes
WHERE schemaname = 'nifty_100';
```

### Performance Monitoring

```sql
-- Slow query log
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
WHERE mean_exec_time > 100
ORDER BY mean_exec_time DESC;
```

---

## Connection String Examples

### psql Command Line

```bash
psql -h localhost -U postgres -d nifty_100 -W
```

### Python (psycopg2)

```python
import psycopg2
conn = psycopg2.connect(
    host="localhost",
    database="nifty_100",
    user="postgres",
    password="password"
)
```

### Node.js (pg)

```javascript
const { Client } = require("pg");
const client = new Client({
  host: "localhost",
  port: 5432,
  database: "nifty_100",
  user: "postgres",
  password: "password",
});
```

### Java (JDBC)

```java
String url = "jdbc:postgresql://localhost:5432/nifty_100";
String user = "postgres";
String password = "password";
Connection conn = DriverManager.getConnection(url, user, password);
```

---

## Useful Queries

### Get Database Size

```sql
SELECT
    schemaname,
    tablename,
    ROUND(pg_total_relation_size(schemaname||'.'||tablename) / 1024.0 / 1024.0, 2) AS size_mb
FROM pg_tables
WHERE schemaname = 'nifty_100'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### Row Counts by Table

```sql
SELECT
    tablename,
    n_live_tup as row_count
FROM pg_stat_user_tables
WHERE schemaname = 'nifty_100'
ORDER BY n_live_tup DESC;
```

### Last Modified Timestamps

```sql
SELECT
    tablename,
    last_vacuum,
    last_autovacuum,
    last_analyze,
    last_autoanalyze
FROM pg_stat_user_tables
WHERE schemaname = 'nifty_100'
ORDER BY tablename;
```

### Data Distribution

```sql
SELECT
    'companies' as table_name,
    COUNT(*) as total_records,
    COUNT(DISTINCT company_id) as unique_ids
FROM companies
UNION ALL
SELECT 'balance_sheet', COUNT(*), COUNT(DISTINCT company_id)
FROM balance_sheet
UNION ALL
SELECT 'profit_and_loss', COUNT(*), COUNT(DISTINCT company_id)
FROM profit_and_loss
UNION ALL
SELECT 'cash_flow', COUNT(*), COUNT(DISTINCT company_id)
FROM cash_flow
UNION ALL
SELECT 'analysis', COUNT(*), COUNT(DISTINCT company_id)
FROM analysis
UNION ALL
SELECT 'documents', COUNT(*), COUNT(DISTINCT company_id)
FROM documents
UNION ALL
SELECT 'prosandcons', COUNT(*), COUNT(DISTINCT proscons_id)
FROM prosandcons;
```

---

## Troubleshooting Quick Links

| Problem             | Likely Cause     | Solution                 |
| ------------------- | ---------------- | ------------------------ |
| FK Constraint Error | Orphaned records | Run data quality checks  |
| Slow Joins          | Missing indexes  | Create composite indexes |
| High Disk Usage     | Large tables     | Archive old data         |
| Connection Refused  | Service down     | Check PostgreSQL service |
| Null Values         | Data quality     | Validate source Excel    |
| Duplicate Records   | Reloads          | Check ETL logic          |

---

## Document References

- **Full Analysis**: `excel_analysis.ipynb` (Jupyter Notebook)
- **Executive Summary**: `ANALYSIS_SUMMARY.md`
- **Technical Spec**: `TECHNICAL_SPECIFICATION.md`
- **ER Diagrams**: `ER_DIAGRAM_AND_RELATIONSHIPS.md`
- **This Guide**: `QUICK_REFERENCE.md` (you are here)

---

## Important Notes

⚠️ **PENDING CLARIFICATION BEFORE IMPLEMENTATION**:

1. Does every DOCUMENTS record link to a COMPANIES record?
2. Is DOCUMENTS.company_id required (NOT NULL) or optional?
3. Are there standalone documents not tied to any company?

✅ **READY FOR IMPLEMENTATION**:

- All other 6 tables have clear relationships
- Primary keys identified
- Foreign keys defined
- Indexes planned
- SQL ready to generate

---

**Last Updated**: May 29, 2026  
**Status**: Design Complete - Ready for Implementation  
**Next Steps**: Database Creation & ETL Development
