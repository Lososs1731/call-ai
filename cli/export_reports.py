"""Export reportů do CSV"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import CallDB
import csv
from datetime import datetime


def export_to_csv(filename='reports.csv'):
    """Exportuje reporty do CSV"""
    db = CallDB()
    
    cursor = db.cursor.execute("""
        SELECT 
            sid,
            phone,
            type,
            classification,
            ai_score,
            summary,
            duration,
            created_at
        FROM calls
        WHERE classification IS NOT NULL
        ORDER BY created_at DESC
    """)
    
    reports = cursor.fetchall()
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Header
        writer.writerow(['Datum', 'Telefon', 'Typ', 'Klasifikace', 'Úspěšnost %', 'Souhrn', 'Trvání (s)'])
        
        # Data
        for r in reports:
            writer.writerow([
                r[7],  # created_at
                r[1],  # phone
                r[2],  # type
                r[3],  # classification
                r[4],  # ai_score
                r[5],  # summary
                r[6]   # duration
            ])
    
    print(f"✅ Exportováno {len(reports)} reportů do {filename}")


if __name__ == "__main__":
    export_to_csv('reports.csv')