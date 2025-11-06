"""
Call Analytics - Databáze a reporting hovorů
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict


class CallAnalytics:
    """Analytika hovorů pro vyhodnocení"""
    
    def __init__(self, db_path='data/calls.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_tables()
    
    def _init_tables(self):
        """Vytvoř tabulky pro analytics"""
        
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS call_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                call_sid TEXT UNIQUE NOT NULL,
                contact_name TEXT,
                contact_phone TEXT,
                company TEXT,
                started_at TIMESTAMP,
                ended_at TIMESTAMP,
                duration INTEGER DEFAULT 0,
                conversation TEXT,
                transcript TEXT,
                outcome TEXT DEFAULT 'unknown',
                got_email BOOLEAN DEFAULT 0,
                got_phone BOOLEAN DEFAULT 0,
                scheduled_callback BOOLEAN DEFAULT 0,
                sales_score INTEGER DEFAULT 0,
                objections_count INTEGER DEFAULT 0,
                positive_signals INTEGER DEFAULT 0,
                ai_summary TEXT,
                ai_recommendations TEXT,
                what_worked TEXT,
                what_failed TEXT,
                campaign TEXT,
                product_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS objections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                call_sid TEXT,
                objection_type TEXT,
                objection_text TEXT,
                ai_response TEXT,
                was_overcome BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS learning_insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                insight_type TEXT,
                context TEXT,
                what_worked TEXT,
                success_rate REAL,
                times_used INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.conn.commit()
    
    def save_call(self, call_data: Dict):
        """Ulož hovor do databáze"""
        
        try:
            print(f"\n[CallAnalytics] save_call()")
            print(f"  Call SID: {call_data.get('call_sid')}")
            print(f"  Outcome: {call_data.get('outcome')}")
            print(f"  Score: {call_data.get('sales_score')}")
            
            self.conn.execute("""
                INSERT OR REPLACE INTO call_details (
                    call_sid, contact_name, contact_phone, company,
                    started_at, ended_at, duration,
                    conversation, transcript,
                    outcome, got_email, got_phone, scheduled_callback,
                    sales_score, objections_count, positive_signals,
                    ai_summary, ai_recommendations, what_worked, what_failed,
                    campaign, product_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                call_data.get('call_sid'),
                call_data.get('contact_name'),
                call_data.get('contact_phone'),
                call_data.get('company'),
                call_data.get('started_at'),
                call_data.get('ended_at'),
                call_data.get('duration', 0),
                json.dumps(call_data.get('conversation', [])),
                call_data.get('transcript', ''),
                call_data.get('outcome', 'unknown'),
                1 if call_data.get('got_email') else 0,
                1 if call_data.get('got_phone') else 0,
                1 if call_data.get('scheduled_callback') else 0,
                call_data.get('sales_score', 0),
                call_data.get('objections_count', 0),
                call_data.get('positive_signals', 0),
                call_data.get('ai_summary', ''),
                call_data.get('ai_recommendations', ''),
                call_data.get('what_worked', ''),
                call_data.get('what_failed', ''),
                call_data.get('campaign', 'default'),
                call_data.get('product_id', 1)
            ))
            
            self.conn.commit()
            print(f"  ✅ COMMIT úspěšný!")
            
            # Ověř že se to uložilo
            cursor = self.conn.execute("SELECT COUNT(*) FROM call_details WHERE call_sid = ?", 
                                    (call_data.get('call_sid'),))
            count = cursor.fetchone()[0]
            print(f"  ✅ Ověření: {count} záznam(ů) s tímto SID")
            
        except Exception as e:
            print(f"  ❌ CHYBA při ukládání: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def get_all_calls(self, limit=100):
        """Získej všechny hovory"""
        
        cursor = self.conn.execute("""
            SELECT * FROM call_details 
            ORDER BY created_at DESC 
            LIMIT ?
        """, (limit,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_stats(self):
        """Získej statistiky"""
        
        cursor = self.conn.execute("""
            SELECT 
                COUNT(*) as total_calls,
                SUM(CASE WHEN outcome = 'success' THEN 1 ELSE 0 END) as successful,
                SUM(CASE WHEN got_email = 1 THEN 1 ELSE 0 END) as got_emails,
                SUM(CASE WHEN got_phone = 1 THEN 1 ELSE 0 END) as got_phones,
                AVG(CASE WHEN sales_score > 0 THEN sales_score ELSE NULL END) as avg_score,
                AVG(CASE WHEN duration > 0 THEN duration ELSE NULL END) as avg_duration,
                SUM(objections_count) as total_objections
            FROM call_details
        """)
        
        row = cursor.fetchone()
        
        return {
            'total_calls': row['total_calls'] or 0,
            'successful': row['successful'] or 0,
            'got_emails': row['got_emails'] or 0,
            'got_phones': row['got_phones'] or 0,
            'avg_score': row['avg_score'] or 0,
            'avg_duration': row['avg_duration'] or 0,
            'total_objections': row['total_objections'] or 0
        }
    
    def print_report(self):
        """Vytiskni report"""
        
        stats = self.get_stats()
        calls = self.get_all_calls(10)
        
        print("\n" + "="*60)
        print("📊 CALL ANALYTICS REPORT")
        print("="*60)
        print(f"📞 Celkem hovorů: {stats['total_calls']}")
        
        if stats['total_calls'] > 0:
            success_rate = (stats['successful'] / stats['total_calls'] * 100)
            print(f"✅ Úspěšné: {stats['successful']} ({success_rate:.1f}%)")
            print(f"📧 Získané emaily: {stats['got_emails']}")
            print(f"📱 Získané telefony: {stats['got_phones']}")
            print(f"⭐ Průměrné skóre: {stats['avg_score']:.1f}/100")
            print(f"⏱️  Průměrná délka: {stats['avg_duration']:.0f}s")
            print(f"⚠️  Celkem námitek: {stats['total_objections']}")
            
            print("\n" + "-"*60)
            print("📋 POSLEDNÍ HOVORY:")
            print("-"*60)
            
            for i, call in enumerate(calls[:5], 1):
                print(f"\n{i}. {call['contact_name'] or 'Neznámý'}")
                print(f"   ⏱️  {call['duration']}s | {call['outcome']}")
                print(f"   ⭐ {call['sales_score']}/100")
                if call['ai_summary']:
                    print(f"   💬 {call['ai_summary'][:80]}...")
        else:
            print("\n⚠️  ZATÍM ŽÁDNÉ HOVORY!")
            print("\n💡 Zavolej na číslo a počkej až hovor skončí.")
        
        print("\n" + "="*60 + "\n")