from bs4 import BeautifulSoup
import requests
import re

departments_voulu = [
    '75',  # Paris
    '91',  # Essonne
    '92',  # Hauts-de-Seine
    '93',  # Seine-Saint-Denis
    '94',  # Val-de-Marne
    '95'   # Val-d'Oise
    
]

class Scraper:
    def fetch(self, url):
        response = requests.get(url)
        return response

    def getAddress(self, response):
        content = BeautifulSoup(response, features="lxml")
        deck = content.find('ul', {'class': 'block-grid large-block-grid-2 small-block-grid-1'})

        residences = {}
        for card in deck.contents:
            if not isinstance(card, str):
                link_tag = card.find('a', class_='visuel-liste')
                link = link_tag['href'] if link_tag and 'href' in link_tag.attrs else None

                address_tag = card.find('div', class_='liste-residence-adresse')
                address = address_tag.text.strip() if address_tag else None

                if link and address:
                    # Ajouter le lien complet
                    if link.startswith('/'):
                        link = f"https://www.fac-habitat.com{link}"
                    residences[address] = link  

        # Filtrer les adresses par département
        self.filter_addresses_by_department(residences, departments_voulu)

    def filter_addresses_by_department(self, residences, departments_voulu):
        matching_addresses = {}

        for address, link in residences.items():
            # Extraire le code postal
            address_parts = address.split('-')
            if len(address_parts) > 1:
                postal_code = address_parts[1].strip().split()[0][:2]
                if postal_code in departments_voulu:
                    matching_addresses[address] = link

        print(f'Nombre de résidences trouvées: {len(matching_addresses)}')
        self.isAvailable(matching_addresses)

    def isAvailable(self, residences):
        available_residences = []

        for address, link in residences.items():
            # Ignorer les liens vers Logifac
            if 'logifac.fr' in link:
                print(f"Ignoring Logifac residence: {address} - Link: {link}")
                continue

            if not link.startswith('https://www.fac-habitat.com/'):
                link = 'https://www.fac-habitat.com/' + link

            try:
                response = requests.get(link, timeout=10)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f"Error fetching residence page: {link}, Error: {e}")
                continue

            soup = BeautifulSoup(response.content, 'html.parser')

            # Trouver l'iframe contenant les informations de réservation
            iframe = soup.find('iframe', {'class': 'reservation'})
            if iframe and 'src' in iframe.attrs:
                iframe_url = iframe['src']

                try:
                    iframe_response = requests.get(iframe_url, timeout=10)
                    iframe_response.raise_for_status()
                except requests.exceptions.RequestException as e:
                    print(f"Error fetching iframe: {iframe_url}, Error: {e}")
                    continue

                iframe_soup = BeautifulSoup(iframe_response.content, 'html.parser')

                # Chercher l'élément <span> contenant la disponibilité
                availability_span = iframe_soup.find('span', {'id': 'avail_area_0'})
                if availability_span:
                    availability_text = availability_span.text.strip()
                    # Vérifier si la résidence est "Disponible" ou "Disponibilité à venir"
                    if "Aucune disponibilité" not in availability_text and (
                        "Disponibilité immédiate" in availability_text or "Disponibilité à venir" in availability_text):
                        available_residences.append({'address': address, 'link': link})
                        continue

        # Afficher uniquement les résidences disponibles ou avec disponibilité à venir
        print(f"Nombre de résidences disponibles ou avec disponibilité à venir: {len(available_residences)}")
        for residence in available_residences:
            print(f"Residence available: {residence['address']} - Link: {residence['link']}")


      
   

    def run(self):
        url = 'https://www.fac-habitat.com/fr/residences-etudiantes?&limit=0'
        res = self.fetch(url)
        self.getAddress(res.text)

if __name__ == '__main__':
    scraper = Scraper()
    scraper.run()
