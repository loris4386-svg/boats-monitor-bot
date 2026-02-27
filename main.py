import logging
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import time
import sys

from config import TELEGRAM_TOKEN, CHAT_ID, CHECK_INTERVAL, PRICE_ITALY_LIMIT
from boats_scraper import BoatsComScraper
from database import YachtDatabase
from telegram_bot import BoatsBot

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BoatsMonitorBot:
    def __init__(self):
        self.scraper = BoatsComScraper()
        self.db = YachtDatabase()
        self.bot = BoatsBot(TELEGRAM_TOKEN, CHAT_ID)
        self.scheduler = BackgroundScheduler()
    
    def check_yachts(self):
        """Esegue il check degli yacht"""
        logger.info("=" * 50)
        logger.info("🔍 Inizio controllo yacht...")
        
        try:
            all_new_yachts = []
            
            # Ricerca yacht sotto 600.000€ in Italia
            logger.info("Ricerca yacht <600k€ in Italia...")
            yachts_italy = self.scraper.search_yachts(
                price_limit=PRICE_ITALY_LIMIT,
                location_filter="italy"
            )
            
            # Ricerca yacht sopra 600.000€ worldwide (escluso USA)
            logger.info("Ricerca yacht >600k€ worldwide...")
            yachts_worldwide = self.scraper.search_yachts(
                price_limit=PRICE_ITALY_LIMIT,
                location_filter="worldwide"
            )
            
            # Combina e filtra i nuovi
            all_yachts = yachts_italy + yachts_worldwide
            new_yachts = self.db.get_new_yachts(all_yachts)
            
            logger.info(f"✅ Trovati {len(new_yachts)} nuovi yacht")
            
            if new_yachts:
                # Invia i nuovi yacht su Telegram
                for yacht in new_yachts:
                    self.bot.send_yacht_message(yacht)
                    time.sleep(0.5)  # Delay per evitare rate limit
                
                # Invia un messaggio riepilogativo
                if len(new_yachts) > 1:
                    time.sleep(1)
                    self.bot.send_batch_message(new_yachts)
            else:
                logger.info("Nessun nuovo yacht trovato")
            
            # Invia status
            stats = self.db.get_stats()
            logger.info(f"Stats: {stats}")
            
        except Exception as e:
            logger.error(f"❌ Errore durante il check: {e}")
            self.bot.send_message(
                chat_id=CHAT_ID,
                text=f"⚠️ Errore nel bot: {str(e)}"
            )
        
        logger.info(f"Prossimo check: {datetime.fromtimestamp(time.time() + CHECK_INTERVAL)}")
        logger.info("=" * 50)
    
    def start(self):
        """Avvia il bot"""
        logger.info("🚀 Bot Boats.com Monitor avviato!")
        logger.info(f"Chat ID: {CHAT_ID}")
        logger.info(f"Intervallo di controllo: {CHECK_INTERVAL // 3600} ore")
        
        # Primo check subito
        self.check_yachts()
        
        # Pianifica i controlli successivi
        self.scheduler.add_job(
            self.check_yachts,
            'interval',
            seconds=CHECK_INTERVAL,
            id='yacht_monitor',
            name='Yacht Monitor'
        )
        
        self.scheduler.start()
        
        logger.info("✅ Scheduler avviato. Bot in ascolto...")
        
        try:
            # Mantieni il bot attivo
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Bot interrotto")
            self.scheduler.shutdown()

if __name__ == '__main__':
    bot = BoatsMonitorBot()
    bot.start()