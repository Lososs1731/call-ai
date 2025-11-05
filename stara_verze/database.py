"""
Databazovy modul pro ukladani hovoru a kontaktu
"""

import sqlite3
import json
from datetime import datetime
from config import Config

class CallDB:
    """Databaze pro ukladani hovoru a kontaktu"""
    
    def __init__(self):
        self.path = Config.DB_PATH
        self._init_tables()
    
    def _init_tables(self):
        """Inicializace databazovych tabulek"""
        conn = sqlite3.connect(self.path)
        cur = conn.cursor()
        
        # Tabulka hovoru
        cur.execute('''CREATE TABLE IF NOT EXISTS calls (
            id INTEGER PRIMARY KEY,
            call_sid TEXT UNIQUE,
            type TEXT,
            direction TEXT,
            phone TEXT,
            start_time TEXT,
            end_time TEXT,
            duration INTEGER,
            status TEXT,
            transcript TEXT,
            outcome TEXT,
            notes TEXT
        )''')
        
        # Tabulka kontaktu
        cur.execute('''CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY,
            name TEXT,
            phone TEXT UNIQUE,
            company TEXT,
            email TEXT,
            status TEXT DEFAULT 'new',
            last_call TEXT,
            call_count INTEGER DEFAULT 0,
            notes TEXT
        )''')
        
        conn.commit()
        conn.close()
    
    def add_call(self, data):
        """Ulozi novy hovor"""
        conn = sqlite3.connect(self.path)
        cur = conn.cursor()
        
        cur.execute('''INSERT OR REPLACE INTO calls 
            (call_sid, type, direction, phone, start_time, status)
            VALUES (?, ?, ?, ?, ?, ?)''',
            (data['sid'], data['type'], data['direction'], 
             data['phone'], datetime.now().isoformat(), 'active'))
        
        conn.commit()
        conn.close()
    
    def update_call(self, sid, updates):
        """Aktualizuje existujici hovor"""
        conn = sqlite3.connect(self.path)
        cur = conn.cursor()
        
        fields = ', '.join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [sid]
        
        cur.execute(f"UPDATE calls SET {fields} WHERE call_sid = ?", values)
        
        conn.commit()
        conn.close()
    
    def add_contact(self, data):
        """Prida novy kontakt"""
        conn = sqlite3.connect(self.path)
        cur = conn.cursor()
        
        try:
            cur.execute('''INSERT INTO contacts 
                (name, phone, company, email)
                VALUES (?, ?, ?, ?)''',
                (data['name'], data['phone'], 
                 data.get('company', ''), data.get('email', '')))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def get_contacts(self, status='new', limit=100):
        """Ziska kontakty pro volani"""
        conn = sqlite3.connect(self.path)
        cur = conn.cursor()
        
        cur.execute('''SELECT id, name, phone, company, email 
                      FROM contacts 
                      WHERE status = ? 
                      LIMIT ?''', (status, limit))
        
        results = cur.fetchall()
        conn.close()
        
        return [{'id': r[0], 'name': r[1], 'phone': r[2], 
                 'company': r[3], 'email': r[4]} for r in results]
    
    def update_contact(self, phone, updates):
        """Aktualizuje kontakt"""
        conn = sqlite3.connect(self.path)
        cur = conn.cursor()
        
        fields = ', '.join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [phone]
        
        cur.execute(f"UPDATE contacts SET {fields} WHERE phone = ?", values)
        
        conn.commit()
        conn.close()
    
    def get_stats(self):
        """Ziska statistiky hovoru"""
        conn = sqlite3.connect(self.path)
        cur = conn.cursor()
        
        cur.execute("SELECT COUNT(*), type FROM calls GROUP BY type")
        results = cur.fetchall()
        
        conn.close()
        
        return {r[1]: r[0] for r in results}