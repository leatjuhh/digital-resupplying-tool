"""
Check PDF batches in database
"""
import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

print("PDF Batches in database:")
print("="*80)

cursor.execute("SELECT id, naam, status, pdf_count, created_at FROM pdf_batches ORDER BY id")
batches = cursor.fetchall()

if not batches:
    print("No batches found in database")
else:
    for batch in batches:
        batch_id, naam, status, pdf_count, created_at = batch
        print(f"ID: {batch_id}")
        print(f"  Naam: {naam}")
        print(f"  Status: {status}")
        print(f"  PDF Count: {pdf_count}")
        print(f"  Created: {created_at}")
        print("-"*80)

conn.close()
