"""
Import znalostí z různých zdrojů
"""

import openai
from config import Config


class KnowledgeImporter:
    """Importuje znalosti z různých zdrojů"""
    
    def import_from_txt(self, filepath, topic_id):
        """Importuje obsah z .txt souboru"""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Ulož do DB
        db.execute("""
            INSERT INTO knowledge_content (topic_id, content, source)
            VALUES (?, ?, ?)
        """, (topic_id, content, filepath))
        
        # Auto-generuj tagy
        tags = self.generate_tags_ai(content)
        for tag, weight in tags:
            db.execute("""
                INSERT INTO tags (topic_id, tag, weight, auto_generated)
                VALUES (?, ?, ?, 1)
            """, (topic_id, tag, weight))
        
        return True
    
    def import_from_url(self, url, topic_id):
        """Scrapuje obsah z webu"""
        import requests
        from bs4 import BeautifulSoup
        
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extrahuj text
        content = soup.get_text()
        
        # Ulož
        db.execute("""
            INSERT INTO knowledge_content (topic_id, content, source)
            VALUES (?, ?, ?)
        """, (topic_id, content, url))
        
        return True
    
    def generate_tags_ai(self, text):
        """Generuje tagy pomocí OpenAI"""
        prompt = f"""Vygeneruj 10 klíčových tagů pro tento text.
        
Text: {text[:500]}...

Vrať JSON: {{"tags": [{{"tag": "název", "weight": 0.9}}, ...]}}
"""
        
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        return [(t['tag'], t['weight']) for t in result['tags']]