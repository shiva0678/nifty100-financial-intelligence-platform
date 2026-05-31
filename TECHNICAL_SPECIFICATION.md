# Technical Specification: NIFTY 100 Database Design

## Document Version: 1.0

**Date**: May 29, 2026  
**Status**: Design Phase - Ready for Implementation  
**Audience**: Data Engineers, Database Administrators, Developers

---

## 1. DATABASE ARCHITECTURE

### 1.1 Schema Model Type

**Star Schema / Dimensional Model**

- Central **COMPANIES** dimension table
- Four **Financial Fact** tables linked to companies
- Supporting reference tables for documents and analysis

### 1.2 Data Organization

```
DIMENSION TABLES:
├── companies (93 records) - MASTER/HUB TABLE

FACT TABLES:
├── balance_sheet (1,313 records) - Quarterly/Annual financial positions
├── profit_and_loss (1,277 records) - Income statement data
├── cash_flow (1,188 records) - Cash movement data
└── analysis (21 records) - Computed financial analysis

REFERENCE/TRANSACTION TABLES:
├── documents (1,586 records) - Supporting documents
└── prosandcons (17 records) - Pros & Cons lookup table
```

### 1.3 Database Characteristics

- **Type**: Relational (SQL)
- **RDBMS**: PostgreSQL 13+
- **Normalization**: Third Normal Form (3NF)
- **Record Volume**: ~5,474 total records
- **Column Count**: 61 total columns
- **Estimated Size**: ~5-10 MB (uncompressed)

---

## 2. TABLE SPECIFICATIONS

### 2.1 COMPANIES (Dimension/Master Table)

**Purpose**: Central repository of all company information  
**Cardinality**: 93 records  
**Record Type**: Master data (slowly changing)

**Column Definitions**:
| Column | Type | Constraint | Purpose | Notes |
|--------|------|-----------|---------|-------|
| company_id | BIGSERIAL | PRIMARY KEY, NOT NULL | Unique identifier | Add if not present |
| company_name | VARCHAR(255) | UNIQUE, NOT NULL | Company name | Index for lookups |
| industry | VARCHAR(100) | | Business sector | For classification |
| [Other columns] | [See notebook] | | [Various attributes] | Full spec in notebook |

**Indexes**:

```sql
PRIMARY KEY (company_id)
UNIQUE INDEX idx_companies_name ON companies(company_name)
INDEX idx_companies_industry ON companies(industry)
```

**Estimated Size**: ~50-100 KB  
**Refresh Frequency**: As needed (master data)  
**Retention Policy**: Keep all historical records

---

### 2.2 BALANCE_SHEET (Fact Table)

**Purpose**: Financial position statements (Assets, Liabilities, Equity)  
**Cardinality**: 1,313 records  
**Record Type**: Transaction data (append-only)  
**Grain**: One row per company per reporting period

**Column Definitions**:
| Column | Type | Constraint | Purpose | Notes |
|--------|------|-----------|---------|-------|
| balance_sheet_id | BIGSERIAL | PRIMARY KEY, NOT NULL | Surrogate key | Required |
| company_id | BIGINT | NOT NULL, FK(companies) | Link to company | Index for join |
| reporting_date | DATE | | Statement date | Critical for analytics |
| total_assets | NUMERIC(15,2) | | Asset sum | Financial metric |
| total_liabilities | NUMERIC(15,2) | | Liability sum | Financial metric |
| total_equity | NUMERIC(15,2) | | Equity sum | Calculated/Derived |
| [Other columns] | [See notebook] | | [Detailed metrics] | See notebook |

**Indexes**:

```sql
PRIMARY KEY (balance_sheet_id)
INDEX idx_bs_company_id ON balance_sheet(company_id)
INDEX idx_bs_reporting_date ON balance_sheet(reporting_date)
INDEX idx_bs_company_date ON balance_sheet(company_id, reporting_date)
FOREIGN KEY (company_id) REFERENCES companies(company_id)
```

**Estimated Size**: ~200-300 KB  
**Refresh Frequency**: Quarterly/Annually  
**Retention Policy**: Keep all historical periods

---

### 2.3 PROFIT_AND_LOSS (Fact Table)

**Purpose**: Income statement data (Revenue, Expenses, Profit)  
**Cardinality**: 1,277 records  
**Record Type**: Transaction data (append-only)  
**Grain**: One row per company per reporting period

**Column Definitions**:
| Column | Type | Constraint | Purpose | Notes |
|--------|------|-----------|---------|-------|
| pl_id | BIGSERIAL | PRIMARY KEY, NOT NULL | Surrogate key | Required |
| company_id | BIGINT | NOT NULL, FK(companies) | Link to company | Index for join |
| reporting_date | DATE | | Statement date | Critical for analytics |
| revenue | NUMERIC(15,2) | | Total income | Key metric |
| cost_of_goods | NUMERIC(15,2) | | COGS | Cost metric |
| operating_expenses | NUMERIC(15,2) | | OpEx | Cost metric |
| net_income | NUMERIC(15,2) | | Bottom line profit | Key metric |
| [Other columns] | [See notebook] | | [Additional metrics] | See notebook |

**Indexes**:

```sql
PRIMARY KEY (pl_id)
INDEX idx_pl_company_id ON profit_and_loss(company_id)
INDEX idx_pl_reporting_date ON profit_and_loss(reporting_date)
INDEX idx_pl_company_date ON profit_and_loss(company_id, reporting_date)
FOREIGN KEY (company_id) REFERENCES companies(company_id)
```

**Estimated Size**: ~200-300 KB  
**Refresh Frequency**: Quarterly/Annually  
**Retention Policy**: Keep all historical periods

---

### 2.4 CASH_FLOW (Fact Table)

**Purpose**: Cash movement statements (Operating, Investing, Financing)  
**Cardinality**: 1,188 records  
**Record Type**: Transaction data (append-only)  
**Grain**: One row per company per reporting period

**Column Definitions**:
| Column | Type | Constraint | Purpose | Notes |
|--------|------|-----------|---------|-------|
| cashflow_id | BIGSERIAL | PRIMARY KEY, NOT NULL | Surrogate key | Required |
| company_id | BIGINT | NOT NULL, FK(companies) | Link to company | Index for join |
| reporting_date | DATE | | Statement date | Critical for analytics |
| operating_cash | NUMERIC(15,2) | | Operating activity | Key metric |
| investing_cash | NUMERIC(15,2) | | Investment activity | Key metric |
| financing_cash | NUMERIC(15,2) | | Financing activity | Key metric |
| net_cash_change | NUMERIC(15,2) | | Total change | Calculated |
| [Other columns] | [See notebook] | | [Additional flows] | See notebook |

**Indexes**:

```sql
PRIMARY KEY (cashflow_id)
INDEX idx_cf_company_id ON cash_flow(company_id)
INDEX idx_cf_reporting_date ON cash_flow(reporting_date)
INDEX idx_cf_company_date ON cash_flow(company_id, reporting_date)
FOREIGN KEY (company_id) REFERENCES companies(company_id)
```

**Estimated Size**: ~150-200 KB  
**Refresh Frequency**: Quarterly/Annually  
**Retention Policy**: Keep all historical periods

---

### 2.5 ANALYSIS (Fact Table)

**Purpose**: Computed financial ratios and analysis  
**Cardinality**: 21 records  
**Record Type**: Derived/Calculated data  
**Grain**: One row per company (or per period)

**Column Definitions**:
| Column | Type | Constraint | Purpose | Notes |
|--------|------|-----------|---------|-------|
| analysis_id | BIGSERIAL | PRIMARY KEY, NOT NULL | Surrogate key | Required |
| company_id | BIGINT | NOT NULL, FK(companies) | Link to company | Index for join |
| metric_name | VARCHAR(100) | | Ratio/metric type | e.g., "P/E Ratio" |
| metric_value | NUMERIC(15,4) | | Calculated value | Ratio value |
| [Other columns] | [See notebook] | | [Analysis data] | See notebook |

**Indexes**:

```sql
PRIMARY KEY (analysis_id)
INDEX idx_analysis_company_id ON analysis(company_id)
FOREIGN KEY (company_id) REFERENCES companies(company_id)
```

**Estimated Size**: ~5-10 KB  
**Refresh Frequency**: As needed  
**Retention Policy**: Keep historical analysis versions

---

### 2.6 DOCUMENTS (Reference Table)

**Purpose**: Supporting documents and files  
**Cardinality**: 1,586 records  
**Record Type**: Transaction data  
**Grain**: One row per document

**Column Definitions** (Preliminary):
| Column | Type | Constraint | Purpose | Notes |
|--------|------|-----------|---------|-------|
| document_id | BIGSERIAL | PRIMARY KEY, NOT NULL | Surrogate key | Required |
| company_id | BIGINT | | Link to company | **TBD: Required or Optional?** |
| document_name | VARCHAR(255) | NOT NULL | Document title | For reference |
| document_type | VARCHAR(50) | | Classification | e.g., "PDF", "Excel" |
| [Other columns] | [See notebook] | | [Document metadata] | See notebook |

**Indexes**:

```sql
PRIMARY KEY (document_id)
INDEX idx_doc_company_id ON documents(company_id) [if FK]
FOREIGN KEY (company_id) REFERENCES companies(company_id) [if required]
```

**⚠️ PENDING CLARIFICATION**:

- Does every document link to a company?
- Is company_id NOT NULL or nullable?
- Are there independent documents?

**Estimated Size**: ~300-400 KB

---

### 2.7 PROSANDCONS (Reference Table)

**Purpose**: Pros and Cons lookup/reference data  
**Cardinality**: 17 records  
**Record Type**: Master/Reference data  
**Grain**: One row per entry

**Column Definitions** (Preliminary):
| Column | Type | Constraint | Purpose | Notes |
|--------|------|-----------|---------|-------|
| proscons_id | BIGSERIAL | PRIMARY KEY, NOT NULL | Surrogate key | Required |
| [Other columns] | [See notebook] | | [Pros/Cons data] | See notebook |

**Indexes**:

```sql
PRIMARY KEY (proscons_id)
```

**Notes**: Small reference table - likely used for lookup/classification  
**Estimated Size**: ~2-5 KB

---

## 3. RELATIONSHIP DEFINITIONS

### 3.1 Primary Relationships

**companies → balance_sheet** (1:N - One-to-Many)

```sql
FOREIGN KEY (company_id) REFERENCES companies(company_id)
Cardinality: 1 company : ~14 balance sheets (1,313 ÷ 93)
```

**companies → profit_and_loss** (1:N)

```sql
FOREIGN KEY (company_id) REFERENCES companies(company_id)
Cardinality: 1 company : ~14 P&L records (1,277 ÷ 93)
```

**companies → cash_flow** (1:N)

```sql
FOREIGN KEY (company_id) REFERENCES companies(company_id)
Cardinality: 1 company : ~13 cash flow records (1,188 ÷ 93)
```

**companies → analysis** (1:N or 1:1)

```sql
FOREIGN KEY (company_id) REFERENCES companies(company_id)
Cardinality: 1 company : <1 analysis record (21 ÷ 93)
```

**companies → documents** (1:N - **Pending Confirmation**)

```sql
FOREIGN KEY (company_id) REFERENCES companies(company_id) [IF APPLICABLE]
Cardinality: 1 company : ~17 documents (1,586 ÷ 93)
```

### 3.2 Relationship Cardinality Summary

| Source      | Target          | Relationship | Ratio | Type       |
| ----------- | --------------- | ------------ | ----- | ---------- |
| companies   | balance_sheet   | 1:N          | 1:14  | Financial  |
| companies   | profit_and_loss | 1:N          | 1:14  | Financial  |
| companies   | cash_flow       | 1:N          | 1:13  | Financial  |
| companies   | analysis        | 1:N          | 1:0.2 | Analytical |
| companies   | documents       | 1:N          | 1:17  | Reference  |
| prosandcons | [TBD]           | ?            | ?     | Lookup     |

---

## 4. DATA QUALITY REQUIREMENTS

### 4.1 Constraints & Validation

**Primary Keys**:

- All tables must have unique, non-null primary key
- Use BIGSERIAL for surrogate keys
- Recommend composite keys where appropriate

**Foreign Keys**:

- All detail tables MUST have company_id FK to companies
- Enforce referential integrity at database level
- Enable ON DELETE RESTRICT to prevent orphaned records

**NOT NULL Constraints**:

- company_id: NOT NULL in all fact tables
- Reporting dates: NOT NULL in financial tables
- Core identifiers: NOT NULL
- See specific table specs above

**UNIQUE Constraints**:

- company_id + reporting_date combinations should be unique in fact tables
- company_name should be unique in companies

### 4.2 Data Validation Checks

**Before Migration**:

- [ ] Verify all company_ids in detail tables exist in companies table
- [ ] Check for null company_ids in fact tables
- [ ] Validate reporting dates are valid DATE values
- [ ] Check numeric fields don't contain text
- [ ] Verify no duplicate company names
- [ ] Validate date ranges (not future-dated)

**During Migration**:

- [ ] Ensure referential integrity constraints are met
- [ ] Monitor for constraint violations
- [ ] Log any data quality issues
- [ ] Create rollback plan if validation fails

**Post-Migration**:

- [ ] Run referential integrity checks
- [ ] Validate record counts match source
- [ ] Sample-verify data accuracy
- [ ] Test common query patterns

---

## 5. INDEXING STRATEGY

### 5.1 Index Types & Purpose

**Surrogate Key Indexes** (Automatic via PRIMARY KEY):

- Speeds primary key lookups
- Required for all tables

**Foreign Key Indexes**:

- CRITICAL for join performance
- Create on company_id in all detail tables
- Example: `INDEX idx_balance_sheet_company_id ON balance_sheet(company_id)`

**Lookup Indexes**:

- company_name in companies table
- industry in companies table

**Range Query Indexes**:

- reporting_date in all financial tables
- Essential for time-range analytics

**Composite Indexes**:

- (company_id, reporting_date) for common joins and filtering

### 5.2 Recommended Indexes

```sql
-- Companies Table
PRIMARY KEY (company_id)
UNIQUE INDEX idx_companies_name ON companies(company_name)
INDEX idx_companies_industry ON companies(industry)

-- Balance Sheet
PRIMARY KEY (balance_sheet_id)
INDEX idx_bs_company_id ON balance_sheet(company_id)
INDEX idx_bs_reporting_date ON balance_sheet(reporting_date)
COMPOSITE INDEX idx_bs_company_date ON balance_sheet(company_id, reporting_date)

-- Profit & Loss
PRIMARY KEY (pl_id)
INDEX idx_pl_company_id ON profit_and_loss(company_id)
INDEX idx_pl_reporting_date ON profit_and_loss(reporting_date)
COMPOSITE INDEX idx_pl_company_date ON profit_and_loss(company_id, reporting_date)

-- Cash Flow
PRIMARY KEY (cashflow_id)
INDEX idx_cf_company_id ON cash_flow(company_id)
INDEX idx_cf_reporting_date ON cash_flow(reporting_date)
COMPOSITE INDEX idx_cf_company_date ON cash_flow(company_id, reporting_date)

-- Analysis
PRIMARY KEY (analysis_id)
INDEX idx_analysis_company_id ON analysis(company_id)

-- Documents
PRIMARY KEY (document_id)
INDEX idx_doc_company_id ON documents(company_id) [if FK exists]

-- Pros & Cons
PRIMARY KEY (proscons_id)
```

---

## 6. PERFORMANCE CONSIDERATIONS

### 6.1 Query Patterns

**Common Joins**:

- Company details with financial statements
- Multi-table financial analysis (BS + P&L + CF)
- Company filtering by industry
- Time-period filtering

**Expected Query Volume**:

- Low transaction rate (batch/daily updates)
- Higher analytical query load
- Suitable for OLAP workloads

### 6.2 Scaling Strategy

**Current Scale**:

- ~5,500 total records (small)
- ~60 columns (moderate width)
- Estimated disk: 5-10 MB (tiny)

**Future Considerations**:

- If company count grows to 1,000+: May need partitioning
- If transaction volume increases 100x: Archival strategy needed
- Historical tracking: Keep all versions (data warehouse)

**No Immediate Scaling Needed** - Current design handles anticipated growth

---

## 7. MIGRATION STRATEGY

### 7.1 Data Loading Sequence

**Phase 1: Master Data**

1. Load companies table first
2. Validate all company_ids are unique, non-null

**Phase 2: Fact Tables** 3. Load balance_sheet (validate FK references) 4. Load profit_and_loss (validate FK references) 5. Load cash_flow (validate FK references) 6. Load analysis (validate FK references)

**Phase 3: Reference Tables** 7. Load documents (clarify FK relationship first) 8. Load prosandcons

### 7.2 Validation Checkpoints

After each phase:

- Count verification (Excel row count = DB row count)
- Sample data spot-checks
- Null value validation
- Date range validation
- FK constraint validation

---

## 8. IMPLEMENTATION CHECKLIST

- [ ] Review and approve schema design
- [ ] Clarify documents table FK relationship
- [ ] Create PostgreSQL database
- [ ] Execute CREATE TABLE scripts
- [ ] Create all indexes
- [ ] Create foreign key constraints
- [ ] Load master data (companies)
- [ ] Validate master data integrity
- [ ] Load fact tables
- [ ] Validate referential integrity
- [ ] Load reference tables
- [ ] Run data quality checks
- [ ] Create views for common queries
- [ ] Document any data issues found
- [ ] Setup backup/recovery procedures
- [ ] Create maintenance scripts
- [ ] Hand off to operations team

---

## 9. OUTSTANDING QUESTIONS & CLARIFICATIONS

1. **Documents Table**:
   - ❓ Does every document link to a company?
   - ❓ Is company_id required or optional?
   - ❓ Are there standalone documents?

2. **Reporting Periods**:
   - ❓ Are all financial statements aligned to same reporting periods?
   - ❓ Any quarterly vs. annual mismatches?

3. **Update Frequency**:
   - ❓ Will data be updated incrementally or full refreshes?
   - ❓ Need to track update dates/audit trail?

4. **Historical Data**:
   - ❓ Keep all historical versions or archive old periods?
   - ❓ Need effective-dated records for slowly changing dimensions?

5. **Data Definitions**:
   - ❓ Need to review actual column names and definitions
   - ❓ Are there calculated columns (derived from other columns)?

---

## 10. RELATED DOCUMENTS

- **Analysis Notebook**: `excel_analysis.ipynb`
- **Summary Report**: `ANALYSIS_SUMMARY.md`
- **Data Dictionary**: [Generated in notebook cells]
- **ER Diagram**: [Mermaid format in notebook]

---

**Document Status**: Draft - Ready for Review  
**Next Step**: Database Implementation with CREATE TABLE scripts  
**Contact**: Senior Data Engineer
