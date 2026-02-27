import os
from dotenv import load_dotenv

load_dotenv()

# Telegram
TELEGRAM_TOKEN = "8519113657:AAEVNapQ2Ds-jl8zGrr2s5Z8OWPlSwhyvfc"
CHAT_ID = 591743494

# Boats.com
BOATS_BASE_URL = "https://www.boats.com"
SEARCH_FILTERS = {
    "type": "motorYacht",  # Yacht a motore
    "listing_type": "private_seller"
}

# Filtri prezzo e ubicazione
PRICE_ITALY_LIMIT = 600000  # € - sopra questo prezzo cerca worldwide
EXCLUDED_COUNTRIES = ["United States", "USA"]

# Database
DB_FILE = "yachts_database.json"
CHECK_INTERVAL = 43200  # 12 ore in secondi