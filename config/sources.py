SOURCES = [
    {
        "url": "https://www.ato.gov.au/individuals-and-families/income-deductions-offsets-and-records/deductions-you-can-claim/work-related-deductions/working-from-home-expenses/fixed-rate-method",
        "income_year": "2025-26"
    }
]

import psycopg
conn = psycopg.connect("postgresql://postgres:postgres@localhost:5432/tax_orchestrator")
print(conn.execute("SELECT version()").fetchone())
conn.close()