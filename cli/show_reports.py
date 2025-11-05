"""
Přehledný viewer AI reportů z kampaně
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import CallDB
import json
from datetime import datetime


def show_campaign_reports(limit=200):
    """Zobrazí přehled všech reportů"""
    
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
        WHERE type = 'outbound'
        ORDER BY created_at DESC
        LIMIT ?
    """, (limit,))
    
    reports = cursor.fetchall()
    
    print(f"\n{'='*120}")
    print(f"📊 PŘEHLED KAMPANĚ - POSLEDNÍ {limit} HOVORŮ")
    print(f"{'='*120}\n")
    
    if not reports:
        print("❌ Žádné hovory nenalezeny")
        return
    
    # Tabulka
    print(f"{'#':<4} {'Datum':<20} {'Telefon':<15} {'Klasifikace':<15} {'Úspěšnost':<12} {'Trvání':<10} {'Souhrn':<40}")
    print(f"{'-'*120}")
    
    for i, r in enumerate(reports, 1):
        date = r[7][:19] if r[7] else 'N/A'
        phone = r[1] or 'N/A'
        classification = (r[3] or 'N/A').upper()
        score = f"{r[4]}%" if r[4] else 'N/A'
        duration = f"{r[7]}s" if r[7] else 'N/A'
        summary = (r[5] or 'N/A')[:40]
        
        # Barvy podle klasifikace
        if classification == 'SUCCESS':
            class_display = f"✅ {classification}"
        elif classification == 'LEAD':
            class_display = f"🔶 {classification}"
        elif classification == 'NO_INTEREST':
            class_display = f"❌ {classification}"
        else:
            class_display = f"⚪ {classification}"
        
        print(f"{i:<4} {date:<20} {phone:<15} {class_display:<20} {score:<12} {duration:<10} {summary:<40}")
    
    print(f"\n{'='*120}")
    
    # STATISTIKY
    total = len(reports)
    
    # Klasifikace
    with_reports = [r for r in reports if r[3]]
    success_count = sum(1 for r in reports if r[3] == 'success')
    lead_count = sum(1 for r in reports if r[3] == 'lead')
    no_interest_count = sum(1 for r in reports if r[3] == 'no_interest')
    unclear_count = sum(1 for r in reports if r[3] == 'unclear')
    no_report_count = total - len(with_reports)
    
    # Průměrná úspěšnost
    avg_score = sum(r[4] for r in reports if r[4]) / len(with_reports) if with_reports else 0
    
    # Průměrná délka
    avg_duration = sum(r[6] for r in reports if r[6]) / total if total > 0 else 0
    
    print(f"\n📈 STATISTIKY KAMPANĚ:")
    print(f"\n🔢 CELKOVÉ:")
    print(f"   Celkem hovorů: {total}")
    print(f"   S AI reportem: {len(with_reports)}")
    print(f"   Bez reportu: {no_report_count}")
    
    print(f"\n📊 KLASIFIKACE:")
    print(f"   ✅ Success: {success_count} ({success_count/total*100:.1f}%)")
    print(f"   🔶 Lead: {lead_count} ({lead_count/total*100:.1f}%)")
    print(f"   ❌ No interest: {no_interest_count} ({no_interest_count/total*100:.1f}%)")
    print(f"   ⚪ Unclear: {unclear_count} ({unclear_count/total*100:.1f}%)")
    
    print(f"\n📉 PRŮMĚRY:")
    print(f"   Úspěšnost: {avg_score:.1f}%")
    print(f"   Délka hovoru: {avg_duration:.0f}s ({avg_duration/60:.1f} min)")
    
    # Conversion rate
    conversion_rate = ((success_count + lead_count) / total * 100) if total > 0 else 0
    print(f"\n💰 CONVERSION RATE:")
    print(f"   (Success + Lead): {conversion_rate:.1f}%")
    
    print(f"\n{'='*120}\n")
    
    # Top 5 nejlepších
    top_success = sorted([r for r in reports if r[4]], key=lambda x: x[4], reverse=True)[:5]
    
    if top_success:
        print(f"🏆 TOP 5 NEJÚSPĚŠNĚJŠÍCH HOVORŮ:")
        for i, r in enumerate(top_success, 1):
            print(f"   {i}. {r[1]} - {r[4]}% - {r[5][:50]}")
        print()


def export_to_csv(filename='campaign_report.csv'):
    """Export reportů do CSV"""
    
    db = CallDB()
    
    cursor = db.cursor.execute("""
        SELECT 
            created_at,
            phone,
            classification,
            ai_score,
            summary,
            duration
        FROM calls
        WHERE type = 'outbound'
        ORDER BY created_at DESC
    """)
    
    reports = cursor.fetchall()
    
    import csv
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Header
        writer.writerow(['Datum', 'Telefon', 'Klasifikace', 'Úspěšnost %', 'Souhrn', 'Trvání (s)'])
        
        # Data
        for r in reports:
            writer.writerow(r)
    
    print(f"✅ Exportováno {len(reports)} hovorů do {filename}")


if __name__ == "__main__":
    
    if len(sys.argv) > 1 and sys.argv[1] == 'export':
        export_to_csv()
    else:
        show_campaign_reports(200)