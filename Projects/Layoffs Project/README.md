# Layoffs Dataset — SQL Data Cleaning & Exploratory Data Analysis (MySQL)

## Overview
This project demonstrates a practical end-to-end SQL workflow using a layoffs dataset.
I created staging tables, cleaned messy real-world fields, and performed exploratory
analysis to identify layoff patterns across companies, industries, countries, and time.

The goal is to showcase SQL skills that are directly relevant to Data Analyst and
Business Analyst work: data cleaning, transformation, and insight generation.

---

## Objectives
- Build a reproducible SQL cleaning pipeline
- Standardize text fields and fix inconsistent values
- Handle null/blank values and remove unusable records
- Convert data types (e.g., date parsing)
- Perform exploratory analysis and trend reporting

---

## Dataset
Input file: `data/layoffs.csv`

Key fields include:
- Company, location, industry, country
- Total laid off, percentage laid off
- Funding raised (millions)
- Date and company stage

---

## Data Cleaning Steps (SQL)
Cleaning was performed using staging tables to keep the raw dataset intact.

### 1) Remove duplicates
- Used `ROW_NUMBER()` with `PARTITION BY` to identify duplicate rows
- Inserted cleaned records into a new staging table

### 2) Standardize values
- Trimmed company names
- Normalized industry categories (e.g., Crypto)
- Standardized country values (removed punctuation / inconsistent naming)

### 3) Handle nulls and blanks
- Converted blank industry values to NULL
- Imputed missing industries by joining on the same company/location
- Removed rows where both `total_laid_off` and `percentage_laid_off` were NULL

### 4) Fix data types
- Converted date strings using `STR_TO_DATE`
- Altered the column type to `DATE`

---

## Exploratory Data Analysis (EDA)
Examples of analysis included:
- Companies with the highest total layoffs
- Layoffs by industry and country
- Full layoffs events (`percentage_laid_off = 1`)
- Monthly totals and rolling cumulative layoffs (window functions)
- Top 5 companies by layoffs per year using `DENSE_RANK()`

---

## SQL Concepts Demonstrated
- Staging tables for safe transformations
- CTEs (`WITH ... AS`)
- Window functions (`ROW_NUMBER`, `SUM OVER`, `DENSE_RANK`)
- JOIN-based imputation for missing categories
- Aggregations, grouping, filtering, ordering

---

## Tools
- SQL (MySQL)

---

## How to Run
1) Create a database (e.g., `layoffs_project`)
2) Load `data/layoffs.csv` into a raw table (e.g., `layoffs`)
3) Run scripts in order:
   - `sql/01_staging.sql`
   - `sql/02_cleaning.sql`
   - `sql/03_eda.sql`

---

## Notes
This project focuses on demonstrating a real analytics workflow (clean → analyze),
rather than building dashboards. Insights can be extended into Tableau/Power BI if needed.

