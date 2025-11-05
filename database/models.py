"""
Databazove modely a operace
"""

import sqlite3
from datetime import datetime
from config import Config


class CallDB:
    """Sprava databaze hovoru a kontaktu"""
    
    def __init__(self):
        self.path = Config.DB_PATH
        self._init_db()
    
    def _init_db(self):
        """Vytvori databazove tabulky"""
        conn = sqlite3.connect(self.path)
        cur = conn.cursor()
        
        # Tabulka hovoru
        cur.execute('''CREATE TABLE IF NOT EXISTS calls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT UNIQUE,
            company TEXT,
            email TEXT,
            status TEXT DEFAULT 'new',
            last_call TEXT,
            call_count INTEGER DEFAULT 0,
            notes TEXT
        )''')
        
        # NOVA: Tabulka produktu/sluzeb
        cur.execute('''CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            description TEXT,
            pitch TEXT,
            price_from INTEGER,
            price_to INTEGER,
            benefits TEXT,
            target_audience TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # NOVA: Tabulka kampani s produktem
        cur.execute('''CREATE TABLE IF NOT EXISTS campaigns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            product_id INTEGER,
            status TEXT DEFAULT 'draft',
            total_contacts INTEGER DEFAULT 0,
            completed_calls INTEGER DEFAULT 0,
            successful_calls INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )''')
        
        conn.commit()
        conn.close()
        
        # Inicializuj defaultni produkt
        self._init_default_product()
    
    def _init_default_product(self):
        """Vytvori defaultni produkt pro tvorbu webu"""
        product = self.get_product_by_name("Tvorba webů na míru")
        
        if not product:
            self.add_product({
                'name': 'Tvorba webů na míru',
                'description': 'Moderní webové stránky kódované ručně od nuly bez šablon',
                'pitch': '''Nabízím tvorbu webových stránek na míru. 
Ruční kódování v HTML, CSS a JavaScript bez šablon pro maximální výkon a SEO.

Co získáte:
- Originální design přesně podle vašich představ
- Rychlé načítání stránek (důležité pro Google)
- SEO optimalizace pro lepší viditelnost
- Mobile-first přístup (funguje na všech zařízeních)
- Technická podpora i po spuštění

Náš proces je jednoduchý:
1. Konzultace vašich požadavků
2. Návrh struktury a funkcionality
3. Ruční vývoj webu
4. Spuštění a následná podpora

Nepoužívám šablony jako WordPress - každý web je unikátní a optimalizovaný.''',
                'price_from': 15000,
                'price_to': 50000,
                'benefits': 'Rychlost, SEO, originální design, technická podpora',
                'target_audience': 'Firmy, podnikatelé, živnostníci potřebující web'
            })
            print("✓ Defaultní produkt 'Tvorba webů' vytvořen")
    
    def add_product(self, data):
        """Prida produkt"""
        conn = sqlite3.connect(self.path)
        cur = conn.cursor()
        
        try:
            cur.execute('''INSERT INTO products 
                (name, description, pitch, price_from, price_to, benefits, target_audience)
                VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (data['name'], data['description'], data['pitch'],
                 data.get('price_from'), data.get('price_to'),
                 data.get('benefits'), data.get('target_audience')))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def get_product_by_name(self, name):
        """Ziska produkt podle nazvu"""
        conn = sqlite3.connect(self.path)
        cur = conn.cursor()
        
        cur.execute('SELECT * FROM products WHERE name = ?', (name,))
        result = cur.fetchone()
        
        conn.close()
        
        if result:
            return {
                'id': result[0],
                'name': result[1],
                'description': result[2],
                'pitch': result[3],
                'price_from': result[4],
                'price_to': result[5],
                'benefits': result[6],
                'target_audience': result[7]
            }
        return None
    
    def get_all_products(self):
        """Ziska vsechny produkty"""
        conn = sqlite3.connect(self.path)
        cur = conn.cursor()
        
        cur.execute('SELECT * FROM products')
        results = cur.fetchall()
        
        conn.close()
        
        return [{'id': r[0], 'name': r[1], 'description': r[2], 
                 'pitch': r[3]} for r in results]
    
    # ... zbytek metod zustava stejny ...
    
    def add_call(self, data):
        """Prida novy hovor"""
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
        """Aktualizuje hovor"""
        conn = sqlite3.connect(self.path)
        cur = conn.cursor()
        
        fields = ', '.join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [sid]
        
        cur.execute(f"UPDATE calls SET {fields} WHERE call_sid = ?", values)
        
        conn.commit()
        conn.close()
    
    def add_contact(self, data):
        """Prida kontakt"""
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
        """Ziska kontakty"""
        conn = sqlite3.connect(self.path)
        cur = conn.cursor()
        
        cur.execute('''SELECT id, name, phone, company, email, call_count
                      FROM contacts 
                      WHERE status = ? 
                      LIMIT ?''', (status, limit))
        
        results = cur.fetchall()
        conn.close()
        
        return [{'id': r[0], 'name': r[1], 'phone': r[2], 
                 'company': r[3], 'email': r[4], 'call_count': r[5]} 
                for r in results]
    
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
        
        cur.execute("SELECT type, COUNT(*) FROM calls GROUP BY type")
        results = cur.fetchall()
        
        conn.close()
        
        return {r[0]: r[1] for r in results}