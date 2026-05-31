# Entity-Relationship Diagram & Data Flow

## ASCII ER Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                    📊 NIFTY 100 DATABASE DESIGN                │
│                        Star Schema Model                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘


                          ╔════════════════╗
                          ║   COMPANIES    ║
                          ║  (93 records)  ║
                          ║  ▲ DIMENSION   ║
                          ╚════════════════╝
                                  │
                    ┌─────────────┼─────────────┐
                    │             │             │
                    │             │             │
                    ▼             ▼             ▼
            ╔════════════════╗ ╔═════════════╗ ╔═════════════╗
            ║ BALANCE_SHEET  ║ ║  PROFIT &   ║ ║  CASH_FLOW  ║
            ║ (1,313 records)║ ║   LOSS      ║ ║(1,188 recs) ║
            ║  ▲ FACT TABLE  ║ ║(1,277 recs) ║ ║ ▲ FACT TABLE║
            ╚════════════════╝ ║ ▲ FACT TABLE║ ╚═════════════╝
                    │          ╚═════════════╝       │
                    │                  │              │
                    └──────────────────┼──────────────┘
                                       │
                          ┌────────────┼────────────┐
                          │            │            │
                          ▼            ▼            ▼
                    ╔═════════════╗ ╔═════════════╗ ╔══════════════╗
                    ║  ANALYSIS   ║ ║ DOCUMENTS   ║ ║PROS & CONS   ║
                    ║(21 records) ║ ║(1,586 recs) ║ ║ (17 records) ║
                    ║ ▲ FACT      ║ ║  Reference? ║ ║  REFERENCE   ║
                    ╚═════════════╝ ╚═════════════╝ ╚══════════════╝


LEGEND:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 ║   ║  Table boundary         1:N  One-to-Many relationship
 ▲    Parent table              ▼   Child table
```

## Detailed Relationship Mapping

### COMPANIES → BALANCE_SHEET (1:N)

```
companies.company_id (PK, UNIQUE)
    │
    ├─ 1 company
    │
    └─────────────────────→ balance_sheet.company_id (FK)
                               │
                               └─ ~14 balance_sheet records per company
                                  (1,313 ÷ 93 ≈ 14.1 avg)
```

**Example Query**:

```sql
SELECT
    c.company_name,
    bs.reporting_date,
    bs.total_assets,
    bs.total_liabilities
FROM companies c
JOIN balance_sheet bs ON c.company_id = bs.company_id
WHERE c.industry = 'Technology'
ORDER BY bs.reporting_date DESC;
```

---

### COMPANIES → PROFIT_AND_LOSS (1:N)

```
companies.company_id (PK, UNIQUE)
    │
    ├─ 1 company
    │
    └─────────────────────→ profit_and_loss.company_id (FK)
                               │
                               └─ ~14 P&L records per company
                                  (1,277 ÷ 93 ≈ 13.7 avg)
```

**Example Query**:

```sql
SELECT
    c.company_name,
    pl.reporting_date,
    pl.revenue,
    pl.net_income,
    (pl.net_income / pl.revenue * 100) AS profit_margin
FROM companies c
JOIN profit_and_loss pl ON c.company_id = pl.company_id
WHERE pl.reporting_date >= '2024-01-01'
ORDER BY profit_margin DESC;
```

---

### COMPANIES → CASH_FLOW (1:N)

```
companies.company_id (PK, UNIQUE)
    │
    ├─ 1 company
    │
    └─────────────────────→ cash_flow.company_id (FK)
                               │
                               └─ ~13 CF records per company
                                  (1,188 ÷ 93 ≈ 12.8 avg)
```

**Example Query**:

```sql
SELECT
    c.company_name,
    cf.reporting_date,
    cf.operating_cash,
    cf.investing_cash,
    cf.financing_cash,
    cf.net_cash_change
FROM companies c
JOIN cash_flow cf ON c.company_id = cf.company_id
WHERE cf.operating_cash > 0
ORDER BY cf.operating_cash DESC
LIMIT 10;
```

---

### COMPANIES → ANALYSIS (1:N or 1:1)

```
companies.company_id (PK, UNIQUE)
    │
    ├─ 1 company
    │
    └─────────────────────→ analysis.company_id (FK)
                               │
                               └─ <1 analysis record per company
                                  (21 ÷ 93 ≈ 0.23 - sparse)
```

**Example Query**:

```sql
SELECT
    c.company_name,
    a.metric_name,
    a.metric_value
FROM companies c
LEFT JOIN analysis a ON c.company_id = a.company_id
WHERE a.metric_name = 'P/E Ratio'
ORDER BY a.metric_value DESC;
```

---

### COMPANIES → DOCUMENTS (1:N - PENDING CLARIFICATION)

```
companies.company_id (PK, UNIQUE)
    │
    ├─ 1 company
    │
    └─────────────────────→ documents.company_id (FK?) ◄─── TBD: Required or Optional?
                               │                         ◄─── TBD: All docs linked?
                               └─ ~17 documents per company
                                  (1,586 ÷ 93 ≈ 17.1 avg)
```

---

### PROSANDCONS (STANDALONE / REFERENCE)

```
Independent reference table
No current relationships identified
│
└─ Purpose: Lookup table for Pros & Cons classification
   ~17 entries
```

---

## Data Flow Diagram

### Analytical Flow

```
Excel Files
    │
    ├─ analysis.xlsx ─────────────────────┐
    ├─ balancesheet.xlsx ────────────────┐│
    ├─ cashflow.xlsx ────────────────────┤├─→ PostgreSQL Database
    ├─ companies.xlsx ──────────────────┐││   Schema: nifty_100
    ├─ documents.xlsx ──────────────────┤││
    ├─ profitandloss.xlsx ──────────────┤││
    └─ prosandcons.xlsx ────────────────┘││
                                          ││
                        ┌─────────────────┘│
                        │                  │
                        ▼                  ▼
                    LOAD ORDER:        TABLES CREATED:
                    1. companies  →    companies (93)
                    2. balance_sheet   balance_sheet (1,313)
                    3. profit_and_loss profit_and_loss (1,277)
                    4. cash_flow   →   cash_flow (1,188)
                    5. analysis    →   analysis (21)
                    6. documents   →   documents (1,586)
                    7. prosandcons →   prosandcons (17)
                                           │
                                           ▼
                                    Data Validation
                                    & Integrity Checks
                                           │
                                           ▼
                                    Analytics Queries
                                    & Reporting
```

---

## Query Patterns & Join Strategy

### 1. Financial Statement Review (Multi-Table Join)

```
GET ALL FINANCIAL DATA FOR A COMPANY

companies
  ├─ JOIN balance_sheet (company_id, reporting_date)
  ├─ JOIN profit_and_loss (company_id, reporting_date)
  ├─ JOIN cash_flow (company_id, reporting_date)
  └─ JOIN analysis (company_id)

Index Strategy:
  - Use (company_id, reporting_date) composite index
  - Query plan: Scan companies → Index lookup on each fact table
  - Expected performance: < 100ms for single company full history
```

### 2. Industry Comparison

```
GET COMPANIES BY INDUSTRY WITH LATEST FINANCIALS

companies
  └─ FILTER BY industry
     └─ JOIN balance_sheet (latest by reporting_date)
     └─ JOIN profit_and_loss (latest by reporting_date)

Index Strategy:
  - Use index on companies.industry
  - Use composite index (company_id, reporting_date DESC)
  - Expected performance: < 500ms for 1 industry
```

### 3. Trend Analysis

```
GET FINANCIAL METRICS OVER TIME FOR ONE COMPANY

balance_sheet / profit_and_loss / cash_flow
  └─ FILTER BY company_id AND reporting_date RANGE
  └─ ORDER BY reporting_date

Index Strategy:
  - Use (company_id, reporting_date) composite index
  - Expected performance: < 200ms for 10 years of data
```

### 4. Performance Ranking

```
GET TOP COMPANIES BY METRIC

profit_and_loss
  ├─ CALCULATE profit_margin = net_income / revenue
  ├─ JOIN companies
  ├─ GROUP BY company_id
  └─ ORDER BY profit_margin DESC

Index Strategy:
  - Full table scan (small table)
  - JOIN on company_id index
  - Expected performance: < 500ms for all companies
```

---

## Cardinality & Scale Analysis

### Record Distribution

```
Table Name              Records    % of Total   Avg Records/Company
─────────────────────────────────────────────────────────────────
companies                   93      1.7%        -
balance_sheet            1,313     23.9%        14.1
profit_and_loss          1,277     23.3%        13.7
cash_flow                1,188     21.7%        12.8
documents                1,586     28.9%        17.1
analysis                    21      0.4%         0.2
prosandcons                 17      0.3%         -
─────────────────────────────────────────────────────────────────
TOTAL                    5,474    100.0%        -
```

### Relationship Multiplicity

| Parent Table | Child Table     | Multiplicity | Example                      |
| ------------ | --------------- | ------------ | ---------------------------- |
| companies    | balance_sheet   | 1:14         | 1 company → ~14 periods      |
| companies    | profit_and_loss | 1:14         | 1 company → ~14 periods      |
| companies    | cash_flow       | 1:13         | 1 company → ~13 periods      |
| companies    | analysis        | 1:0.2        | 1 company → partial coverage |
| companies    | documents       | 1:17         | 1 company → ~17 documents    |

---

## Data Model Characteristics

### ✅ Strengths

1. **Clear Hub-and-Spoke Pattern**
   - Single source of truth: Companies table
   - All facts traceable to company
   - Easy to understand and navigate

2. **Denormalized for Performance**
   - Each fact table contains all needed context
   - Minimal joins required
   - Query optimization straightforward

3. **Time-Series Ready**
   - Reporting dates in all fact tables
   - Supports historical analysis
   - Easy trend calculations

4. **Industry Classification**
   - Dimension table (companies) has industry field
   - Enables industry-based analytics
   - Good for comparative analysis

### ⚠️ Considerations

1. **Data Redundancy**
   - Company info duplicated in each fact record
   - Trade-off: Denormalization for query performance
   - Acceptable for data warehouse model

2. **Update Complexity**
   - Company changes require multi-table updates
   - Mitigated by low update frequency
   - Could implement SCD Type 2 if needed

3. **Sparse Analytics Table**
   - Only ~18% coverage in analysis table
   - May indicate incomplete calculations
   - Recommend clarifying data completeness

4. **Document Table Ambiguity**
   - Relationship to companies unclear
   - **ACTION**: Clarify before final implementation

---

## Visual SQL Join Tree

```
CORPORATE FINANCIAL ANALYSIS QUERY STRUCTURE

                        ┌─────────────────────────────┐
                        │  START: companies (93)      │
                        │  WHERE industry = 'Tech'    │
                        └──────────┬──────────────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    │              │              │
                    ▼              ▼              ▼
          ┌──────────────────┐ ┌──────────────┐ ┌─────────────────┐
          │ balance_sheet    │ │profit_and_loss│ │   cash_flow    │
          │ (latest period)  │ │(latest period)│ │ (latest period)│
          │ ▲ FK: company_id │ │▲ FK: company_id│ │▲ FK: company_id│
          └──────────────────┘ └──────────────┘ └─────────────────┘
                    │              │              │
                    └──────────────┴──────────────┘
                                   │
                                   ▼
                    ┌──────────────────────────────┐
                    │ OUTPUT: Financial Dashboard  │
                    │ - Assets & Liabilities       │
                    │ - Revenue & Net Income       │
                    │ - Cash Position              │
                    │ - Calculated Ratios          │
                    └──────────────────────────────┘
```

---

## Implementation Notes

### For Query Optimization

- Always filter on companies table first (smallest)
- Use composite indexes for (company_id, reporting_date) joins
- Consider materialized views for common multi-table queries
- Archive old reporting periods if dataset grows

### For Data Quality

- Validate all company_ids exist in companies table
- Check reporting_date consistency across tables
- Monitor for duplicate entries
- Track data lineage and source

### For Scaling

- Current design handles ~100K+ records easily
- If exceeding 10M records, consider:
  - Table partitioning by reporting_date
  - Separate reporting database (OLAP)
  - Data aggregation/summarization

---

_Last Updated: May 29, 2026_  
_Status: Design Phase - Ready for Implementation_
