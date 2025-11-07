"""
MySQL Znalostní báze s AI learningem
"""

import mysql.connector
from typing import List, Dict, Optional
import json
from datetime import datetime


class KnowledgeBase:
    """MySQL znalostní báze"""
    
    def __init__(self):
        self.conn = mysql.connector.connect(
            host='localhost',
            user='root',  # ✅ ZMĚŇ NA SVOJE!
            password='',  # ✅ ZMĚŇ NA SVOJE!
            database='ai_calling',
            charset='utf8mb4'
        )
        self.cursor = self.conn.cursor(dictionary=True)
    
    def get_best_response(self, category: str, topic: str, context: str = None) -> Optional[str]:
        """Získej nejlepší odpověď z znalostní báze"""
        
        query = """
            SELECT answer, success_rate, times_used
            FROM knowledge_base
            WHERE category = %s AND topic = %s
        """
        params = [category, topic]
        
        if context:
            query += " AND context = %s"
            params.append(context)
        
        query += " ORDER BY success_rate DESC, times_used DESC LIMIT 1"
        
        self.cursor.execute(query, params)
        result = self.cursor.fetchone()
        
        if result:
            # Zaznamenaj použití
            self._mark_used(category, topic, context)
            return result['answer']
        
        return None
    
    def get_objection_response(self, customer_phrase: str) -> Optional[str]:
        """Najdi nejlepší odpověď na námitku"""
        
        # Hledej podobné fráze
        self.cursor.execute("""
            SELECT objection_type, bot_response, success_rate
            FROM objection_responses
            WHERE LOWER(%s) LIKE CONCAT('%%', LOWER(customer_phrase), '%%')
            ORDER BY success_rate DESC, times_used DESC
            LIMIT 1
        """, (customer_phrase,))
        
        result = self.cursor.fetchone()
        
        if result:
            self._mark_objection_used(result['objection_type'])
            return result['bot_response']
        
        return None
    
    def get_successful_phrase(self, phrase_type: str) -> Optional[str]:
        """Získej nejúspěšnější frázi daného typu"""
        
        self.cursor.execute("""
            SELECT phrase_text
            FROM successful_phrases
            WHERE phrase_type = %s
            ORDER BY success_rate DESC, conversions DESC
            LIMIT 1
        """, (phrase_type,))
        
        result = self.cursor.fetchone()
        return result['phrase_text'] if result else None
    
    def learn_from_call(self, call_data: Dict):
        """Uč se z hovoru - úspěšného i neúspěšného"""
        
        outcome = call_data.get('outcome')
        score = call_data.get('sales_score', 0)
        conversation = call_data.get('conversation', [])
        
        if score >= 70:
            # ÚSPĚŠNÝ HOVOR - ulož co fungovalo
            self._learn_success(call_data)
        elif score < 40:
            # NEÚSPĚŠNÝ HOVOR - ulož co selhalo
            self._learn_failure(call_data)
        
        # Aktualizuj success rates
        self._update_success_rates(call_data)
    
    def _learn_success(self, call_data: Dict):
        """Uč se z úspěšného hovoru"""
        
        what_worked = call_data.get('what_worked', '')
        
        if what_worked:
            self.cursor.execute("""
                INSERT INTO learning_insights (
                    insight_type, situation, what_worked, recommendation, confidence_score
                ) VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    times_applied = times_applied + 1,
                    success_when_applied = success_when_applied + 1
            """, (
                'success_pattern',
                call_data.get('ai_summary', ''),
                what_worked,
                f"Použij: {what_worked}",
                call_data.get('sales_score', 0) / 100.0
            ))
            
            self.conn.commit()
    
    def _learn_failure(self, call_data: Dict):
        """Uč se z neúspěšného hovoru"""
        
        what_failed = call_data.get('what_failed', '')
        recommendations = call_data.get('ai_recommendations', '')
        
        if what_failed:
            self.cursor.execute("""
                INSERT INTO learning_insights (
                    insight_type, situation, what_failed, recommendation, confidence_score
                ) VALUES (%s, %s, %s, %s, %s)
            """, (
                'failure_pattern',
                call_data.get('ai_summary', ''),
                what_failed,
                recommendations,
                0.5
            ))
            
            self.conn.commit()
    
    def _mark_used(self, category: str, topic: str, context: str = None):
        """Zaznamenaj že odpověď byla použita"""
        
        query = """
            UPDATE knowledge_base
            SET times_used = times_used + 1, last_used = NOW()
            WHERE category = %s AND topic = %s
        """
        params = [category, topic]
        
        if context:
            query += " AND context = %s"
            params.append(context)
        
        self.cursor.execute(query, params)
        self.conn.commit()
    
    def _mark_objection_used(self, objection_type: str):
        """Zaznamenaj použití odpovědi na námitku"""
        
        self.cursor.execute("""
            UPDATE objection_responses
            SET times_used = times_used + 1
            WHERE objection_type = %s
        """, (objection_type,))
        
        self.conn.commit()
    
    def _update_success_rates(self, call_data: Dict):
        """Aktualizuj success rates podle výsledku"""
        
        # TODO: Implementuj logiku pro aktualizaci success_rate
        # na základě toho jestli hovor byl úspěšný
        pass
    
    def get_all_learnings(self, limit: int = 100) -> List[Dict]:
        """Získej všechny naučené insighty"""
        
        self.cursor.execute("""
            SELECT *
            FROM learning_insights
            ORDER BY confidence_score DESC, created_at DESC
            LIMIT %s
        """, (limit,))
        
        return self.cursor.fetchall()
    
    def close(self):
        """Zavři spojení"""
        self.cursor.close()
        self.conn.close()