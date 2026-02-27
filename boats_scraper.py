import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BoatsComScraper:
    def __init__(self):
        self.base_url = "https://www.boats.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def search_yachts(self, price_limit, location_filter=None):
        """Cerca yacht a motore su boats.com
        price_limit: limite di prezzo in €
        location_filter: 'italy' o 'worldwide'
        """
        yachts = []
        
        try:
            # URL di ricerca per yacht a motore - venditori privati
            if location_filter == "italy":
                search_url = f"{self.base_url}/boats-for-sale?type=motorYacht&price_max={price_limit}&location=IT&listing_type=private"
            else:
                search_url = f"{self.base_url}/boats-for-sale?type=motorYacht&price_min={price_limit}&listing_type=private"
            
            logger.info(f"Scraping: {search_url}")
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Cerca i card degli annunci
            yacht_listings = soup.find_all('div', class_='listing-card')
            
            if not yacht_listings:
                # Alternativa se la struttura HTML è diversa
                yacht_listings = soup.find_all('article', class_='vessel-card')
            
            for listing in yacht_listings:
                yacht_data = self._parse_yacht_listing(listing)
                if yacht_data:
                    # Filtra paesi esclusi se price >= 600.000
                    if location_filter == "worldwide" and price_limit >= 600000:
                        if self._is_excluded_country(yacht_data.get('location', '')):
                            continue
                    
                    yachts.append(yacht_data)
            
            logger.info(f"Trovati {len(yachts)} yacht")
            return yachts
        
        except Exception as e:
            logger.error(f"Errore durante lo scraping: {e}")
            return []
    
    def _parse_yacht_listing(self, listing):
        """Estrae i dati da un singolo annuncio"""
        try:
            # Estrai i dati (adattare ai selettori reali di boats.com)
            title = listing.find('h2', class_='listing-title')
            price = listing.find('span', class_='listing-price')
            location = listing.find('span', class_='listing-location')
            image = listing.find('img', class_='listing-image')
            link = listing.find('a', class_='listing-link')
            year = listing.find('span', class_='year')
            length = listing.find('span', class_='length')
            
            if not title or not link:
                return None
            
            # Estrai il prezzo in €
            price_text = price.text.strip() if price else "N/A"
            price_value = self._extract_price(price_text)
            
            yacht = {
                'id': self._generate_id(link.get('href', '')),
                'title': title.text.strip(),
                'price': price_text,
                'price_value': price_value,
                'location': location.text.strip() if location else "Non specificata",
                'year': year.text.strip() if year else "N/A",
                'length': length.text.strip() if length else "N/A",
                'description': self._get_description(listing),
                'image_url': image.get('src', '') if image else '',
                'link': link.get('href', ''),
                'found_at': datetime.now().isoformat(),
                'seller_type': 'Private Seller'
            }
            
            return yacht
        
        except Exception as e:
            logger.error(f"Errore nel parsing: {e}")
            return None
    
    def _extract_price(self, price_text):
        """Estrae il valore numerico del prezzo"""
        import re
        # Cerca numeri nel testo
        match = re.search(r'[\d.,]+', price_text.replace('.', '').replace(',', ''))
        if match:
            try:
                return int(match.group())
            except:
                return 0
        return 0
    
    def _get_description(self, listing):
        """Estrae la descrizione dell'annuncio"""
        desc = listing.find('p', class_='listing-description')
        if desc:
            return desc.text.strip()[:200]  # Prime 200 caratteri
        return ""
    
    def _generate_id(self, url):
        """Genera un ID univoco dall'URL"""
        import hashlib
        return hashlib.md5(url.encode()).hexdigest()[:12]
    
    def _is_excluded_country(self, location):
        """Controlla se la location è negli USA"""
        excluded = ["USA", "United States", "America"]
        return any(country.lower() in location.lower() for country in excluded)