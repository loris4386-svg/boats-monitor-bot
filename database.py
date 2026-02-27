import json
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class YachtDatabase:
    def __init__(self, db_file='yachts_database.json'):
        self.db_file = db_file
        self.load_database()
    
    def load_database(self):
        """Carica il database dal file JSON"""
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
            except Exception as e:
                logger.error(f"Errore caricamento database: {e}")
                self.data = {'yachts': {}, 'last_check': None}
        else:
            self.data = {'yachts': {}, 'last_check': None}
    
    def save_database(self):
        """Salva il database nel file JSON"""
        try:
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            logger.info("Database salvato")
        except Exception as e:
            logger.error(f"Errore salvataggio database: {e}")
    
    def get_new_yachts(self, current_yachts):
        """Confronta gli yacht attuali con il database e restituisce i nuovi"""
        new_yachts = []
        
        for yacht in current_yachts:
            yacht_id = yacht.get('id')
            if yacht_id not in self.data['yachts']:
                new_yachts.append(yacht)
                self.data['yachts'][yacht_id] = yacht
        
        self.data['last_check'] = datetime.now().isoformat()
        self.save_database()
        
        return new_yachts
    
    def get_stats(self):
        """Restituisce le statistiche del database"""
        return {
            'total_yachts': len(self.data['yachts']),
            'last_check': self.data.get('last_check', 'Mai'),
            'db_file': self.db_file
        }