"""
Služba pro práci se znalostní bází
"""

class KnowledgeService:
    """Načítá znalosti z databáze"""
    
    def search_knowledge(self, query):
        """Hledá relevantní znalosti podle dotazu"""
        
        # 1. Najdi relevantní témata (fulltext search)
        cursor = db.execute("""
            SELECT t.name, k.content
            FROM topics t
            JOIN knowledge_content k ON k.topic_id = t.id
            WHERE k.content LIKE ? AND t.active = 1
            LIMIT 3
        """, (f'%{query}%',))
        
        results = cursor.fetchall()
        
        # 2. Poskládej kontext pro AI
        context = "\n\n".join([
            f"TÉMA: {r[0]}\n{r[1][:500]}..."
            for r in results
        ])
        
        return context
    
    def get_active_categories(self):
        """Vrátí aktivní kategorie"""
        cursor = db.execute("""
            SELECT id, name, description
            FROM categories
            WHERE active = 1
        """)
        return cursor.fetchall()