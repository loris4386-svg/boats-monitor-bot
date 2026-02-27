from telegram import Bot, ParseMode
from telegram.error import TelegramError
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class BoatsBot:
    def __init__(self, token, chat_id):
        self.bot = Bot(token=token)
        self.chat_id = chat_id
    
    def send_yacht_message(self, yacht):
        """Invia i dettagli di uno yacht via Telegram"""
        try:
            # Formatta il messaggio
            message = self._format_yacht_message(yacht)
            
            # Invia foto se disponibile
            if yacht.get('image_url'):
                try:
                    self.bot.send_photo(
                        chat_id=self.chat_id,
                        photo=yacht['image_url'],
                        caption=message,
                        parse_mode=ParseMode.HTML
                    )
                except:
                    # Se la foto non è disponibile, invia solo testo
                    self.bot.send_message(
                        chat_id=self.chat_id,
                        text=message,
                        parse_mode=ParseMode.HTML
                    )
            else:
                self.bot.send_message(
                    chat_id=self.chat_id,
                    text=message,
                    parse_mode=ParseMode.HTML
                )
            
            logger.info(f"Messaggio inviato per: {yacht['title']}")
            return True
        
        except TelegramError as e:
            logger.error(f"Errore Telegram: {e}")
            return False
    
    def send_batch_message(self, yachts):
        """Invia un messaggio riepilogativo con più yacht"""
        if not yachts:
            return False
        
        try:
            message = "<b>🚤 NUOVI YACHT TROVATI!</b>\n\n"
            
            for i, yacht in enumerate(yachts, 1):
                message += f"<b>{i}. {yacht['title']}</b>\n"
                message += f"💰 Prezzo: {yacht['price']}\n"
                message += f"📍 Ubicazione: {yacht['location']}\n"
                message += f"📏 Lunghezza: {yacht['length']}\n"
                message += f"📅 Anno: {yacht['year']}\n"
                message += f"🔗 <a href='{yacht['link']}'>Visualizza Annuncio</a>\n"
                message += "─" * 40 + "\n\n"
            
            self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=False
            )
            
            logger.info(f"Batch message inviato con {len(yachts)} yacht")
            return True
        
        except TelegramError as e:
            logger.error(f"Errore Telegram batch: {e}")
            return False
    
    def _format_yacht_message(self, yacht):
        """Formatta i dettagli dello yacht in HTML"""
        message = f"""
<b>🚤 {yacht['title']}</b>\n
<b>Prezzo:</b> {yacht['price']}\n<b>Ubicazione:</b> {yacht['location']}\n<b>Anno:</b> {yacht['year']}\n<b>Lunghezza:</b> {yacht['length']}\n<b>Venditore:</b> {yacht['seller_type']}\n
<b>Descrizione:</b>\n{yacht['description']}\n
<a href="{yacht['link']}">🔗 Visualizza Annuncio Completo</a>\n"""
        return message
    
    def send_status_message(self, stats):
        """Invia un messaggio di status"""
        try:
            message = f"""
<b>📊 STATUS BOT</b>\n
Total yacht registrati: {stats['total_yachts']}\nUltimo controllo: {stats['last_check']}\nDatabase: {stats['db_file']}\n
✅ Bot attivo e funzionante!\n"""
            self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode=ParseMode.HTML
            )
            return True
        except TelegramError as e:
            logger.error(f"Errore invio status: {e}")
            return False