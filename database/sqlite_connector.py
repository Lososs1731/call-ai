"""
SQLite Connector pro Knowledge Base
Připojení k database/knowledge_base.db
"""

import sqlite3
import os
from typing import Optional, Dict, List, Tuple
from contextlib import contextmanager

class SQLiteConnector:
    """Správa připojení k SQLite databázi"""
    
    def __init__(self, db_path: str = 'database/knowledge_base.db'):
        self.db_path = db_path
        
        # Ověř že databáze existuje
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(
                f"❌ Databáze nenalezena: {self.db_path}\n"
                f"Spusť nejprve: python database/create_complete_sqlite.py"
            )
        
        print(f"✅ SQLite připojeno: {self.db_path}")
    
    @contextmanager
    def get_connection(self):
        """Context manager pro bezpečné připojení"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Vrací Row objekty místo tuples
        try:
            yield conn
        finally:
            conn.close()
    
    def execute_query(self, query: str, params: tuple = ()) -> List[sqlite3.Row]:
        """Spusť SELECT query a vrať výsledky"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """Spusť UPDATE/INSERT a vrať počet ovlivněných řádků"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount


class KnowledgeBase:
    """Hlavní interface pro práci s knowledge base"""
    
    def __init__(self):
        self.db = SQLiteConnector()
        self._load_stats()
    
    def _load_stats(self):
        """Načti základní statistiky"""
        stats = {
            'topics': self.db.execute_query("SELECT COUNT(*) as c FROM allowed_topics")[0]['c'],
            'redirects': self.db.execute_query("SELECT COUNT(*) as c FROM redirect_templates")[0]['c'],
            'responses': self.db.execute_query("SELECT COUNT(*) as c FROM cold_call_responses")[0]['c'],
            'phrases': self.db.execute_query("SELECT COUNT(*) as c FROM czech_natural_phrases")[0]['c'],
        }
        print(f"📊 Knowledge Base loaded:")
        print(f"   • {stats['topics']} topics")
        print(f"   • {stats['redirects']} redirect templates")
        print(f"   • {stats['responses']} call responses")
        print(f"   • {stats['phrases']} české fráze")
    
    # ============================================================
    # TOPICS (OFF-TOPIC DETECTION)
    # ============================================================
    
    def get_all_topics(self) -> List[Dict]:
        """Získej všechny whitelisted topics"""
        rows = self.db.execute_query("""
            SELECT * FROM allowed_topics
            ORDER BY priority DESC, is_core_topic DESC
        """)
        return [dict(row) for row in rows]
    
    def is_on_topic(self, text: str) -> Tuple[bool, Optional[str]]:
        """
        Zkontroluj jestli text je ON-TOPIC
        Returns: (is_on_topic: bool, matched_topic: str)
        """
        topics = self.get_all_topics()
        
        text_lower = text.lower()
        
        for topic in topics:
            keywords = topic['on_topic_keywords'].lower().split(',')
            keywords = [k.strip() for k in keywords]
            
            for keyword in keywords:
                if keyword in text_lower:
                    return True, topic['topic_name']
        
        return False, None
    
    # ============================================================
    # REDIRECTS (OFF-TOPIC → ON-TOPIC)
    # ============================================================
    
    def get_redirect(self, redirect_type: str = 'general_offtopic') -> Optional[Dict]:
        """Získej redirect template"""
        rows = self.db.execute_query("""
            SELECT * FROM redirect_templates
            WHERE redirect_type = ?
            ORDER BY success_rate DESC
            LIMIT 1
        """, (redirect_type,))
        
        if rows:
            return dict(rows[0])
        
        # Fallback na general
        rows = self.db.execute_query("""
            SELECT * FROM redirect_templates
            WHERE redirect_type = 'general_offtopic'
            LIMIT 1
        """)
        return dict(rows[0]) if rows else None
    
    # ============================================================
    # RESPONSES (COLD CALLING)
    # ============================================================
    
    def get_best_response(
        self, 
        stage: str,
        sub_category: Optional[str] = None,
        situation: Optional[str] = None,
        limit: int = 3
    ) -> List[Dict]:
        """
        Získej nejlepší response pro danou situaci
        
        Args:
            stage: intro/discovery/value/objection/closing
            sub_category: upřesnění (time_sensitive, no_money, ...)
            situation: konkrétní situace
            limit: kolik variant vrátit
        """
        
        # Build query
        query = """
            SELECT * FROM cold_call_responses
            WHERE call_stage = ?
        """
        params = [stage]
        
        if sub_category:
            query += " AND sub_category = ?"
            params.append(sub_category)
        
        if situation:
            query += " AND situation LIKE ?"
            params.append(f"%{situation}%")
        
        query += """
            ORDER BY 
                success_rate DESC,
                conversion_rate DESC,
                times_used ASC
            LIMIT ?
        """
        params.append(limit)
        
        rows = self.db.execute_query(query, tuple(params))
        return [dict(row) for row in rows]
    
    def get_response_by_stage(self, stage: str, limit: int = 5) -> List[Dict]:
        """Získej top responses pro daný stage"""
        rows = self.db.execute_query("""
            SELECT * FROM cold_call_responses
            WHERE call_stage = ?
            ORDER BY success_rate DESC, conversion_rate DESC
            LIMIT ?
        """, (stage, limit))
        return [dict(row) for row in rows]
    
    def get_random_response(self, stage: str) -> Optional[Dict]:
        """Získej náhodnou response (pro variabilitu)"""
        rows = self.db.execute_query("""
            SELECT * FROM cold_call_responses
            WHERE call_stage = ?
            ORDER BY RANDOM()
            LIMIT 1
        """, (stage,))
        return dict(rows[0]) if rows else None
    
    # ============================================================
    # ČESKÉ FRÁZE
    # ============================================================
    
    def get_czech_phrases(
        self, 
        phrase_type: Optional[str] = None,
        frequency: str = 'high'
    ) -> List[Dict]:
        """
        Získej české fráze pro přirozený hovor
        
        Args:
            phrase_type: filler/transition/agreement/empathy/...
            frequency: high/medium/low
        """
        query = "SELECT * FROM czech_natural_phrases WHERE 1=1"
        params = []
        
        if phrase_type:
            query += " AND phrase_type = ?"
            params.append(phrase_type)
        
        if frequency:
            query += " AND frequency = ?"
            params.append(frequency)
        
        query += " ORDER BY natural_score DESC"
        
        rows = self.db.execute_query(query, tuple(params))
        return [dict(row) for row in rows]
    
    def get_random_filler(self) -> Optional[str]:
        """Získej náhodný český filler (no, jo, jasně, ...)"""
        rows = self.db.execute_query("""
            SELECT czech_phrase FROM czech_natural_phrases
            WHERE phrase_type = 'filler' AND frequency = 'high'
            ORDER BY RANDOM()
            LIMIT 1
        """)
        return rows[0]['czech_phrase'] if rows else None
    
    # ============================================================
    # LEARNING (UKLÁDÁNÍ ZPĚT)
    # ============================================================
    
    def log_response_usage(
        self, 
        response_id: int,
        was_successful: bool = False,
        led_to_meeting: bool = False
    ):
        """
        Zaloguj použití response a update metriky
        
        Args:
            response_id: ID použité response
            was_successful: Zákazník pozitivně reagoval?
            led_to_meeting: Vedlo to k domluvení schůzky?
        """
        
        # Update times_used
        self.db.execute_update("""
            UPDATE cold_call_responses
            SET times_used = times_used + 1,
                last_used = datetime('now')
            WHERE id = ?
        """, (response_id,))
        
        # Update meeting count
        if led_to_meeting:
            self.db.execute_update("""
                UPDATE cold_call_responses
                SET times_led_to_meeting = times_led_to_meeting + 1
                WHERE id = ?
            """, (response_id,))
        
        # Recalculate success_rate and conversion_rate
        self.db.execute_update("""
            UPDATE cold_call_responses
            SET 
                success_rate = CASE 
                    WHEN times_used > 0 
                    THEN CAST(times_led_to_meeting AS REAL) / times_used * 100
                    ELSE 50.0
                END,
                conversion_rate = CASE
                    WHEN times_used > 0
                    THEN CAST(times_led_to_meeting AS REAL) / times_used * 100
                    ELSE 0.0
                END
            WHERE id = ?
        """, (response_id,))
        
        print(f"📊 Response #{response_id} usage logged (meeting: {led_to_meeting})")
    
    def log_redirect_usage(self, redirect_id: int, was_successful: bool):
        """Zaloguj použití redirectu"""
        self.db.execute_update("""
            UPDATE redirect_templates
            SET times_used = times_used + 1,
                times_successful = times_successful + ?
            WHERE id = ?
        """, (1 if was_successful else 0, redirect_id))
        
        # Update success_rate
        self.db.execute_update("""
            UPDATE redirect_templates
            SET success_rate = CASE
                WHEN times_used > 0
                THEN CAST(times_successful AS REAL) / times_used * 100
                ELSE 50.0
            END
            WHERE id = ?
        """, (redirect_id,))
    
    # ============================================================
    # STATS
    # ============================================================
    
    def get_top_performing_responses(self, limit: int = 10) -> List[Dict]:
        """Získej top performing responses"""
        rows = self.db.execute_query("""
            SELECT * FROM cold_call_responses
            WHERE times_used >= 3
            ORDER BY conversion_rate DESC, success_rate DESC
            LIMIT ?
        """, (limit,))
        return [dict(row) for row in rows]
    
    def get_stage_stats(self) -> Dict[str, int]:
        """Získej statistiky podle stage"""
        rows = self.db.execute_query("""
            SELECT call_stage, COUNT(*) as count
            FROM cold_call_responses
            GROUP BY call_stage
        """)
        return {row['call_stage']: row['count'] for row in rows}


# ============================================================
# SINGLETON INSTANCE
# ============================================================

_kb_instance = None

def get_knowledge_base() -> KnowledgeBase:
    """Získej singleton instance knowledge base"""
    global _kb_instance
    if _kb_instance is None:
        _kb_instance = KnowledgeBase()
    return _kb_instance