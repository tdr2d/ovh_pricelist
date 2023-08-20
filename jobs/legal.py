from utils import *
import bs4
import re

LEGALS = [
    {'key': '1', 'text': 'Baremetal', 'url': 'https://contract.eu.ovhapis.com/1.0/pdf/contrat_partDedie-fr.pdf'},
    {'key': '2', 'text': 'Private Cloud', 'url': 'https://contract.eu.ovhapis.com/1.0/pdf/HPCPremier-fr.pdf'},
    {'key': '3', 'text': 'Public Cloud', 'url': ''},
    {'key': '4', 'text': 'OVHCloud Connect', 'url': ''},
    {'key': '5', 'text': 'Windows SPLA', 'url': 'https://storage.gra.cloud.ovh.net/v1/AUTH_325716a587c64897acbef9a4a4726e38/contracts/93af107-EULA_MCSFT_VPS_PCI-ALL-1.0.pdf'},
    {'key': '6', 'text': 'Bring Your Own IP (BYOIP)', 'url': 'https://storage.gra.cloud.ovh.net/v1/AUTH_325716a587c64897acbef9a4a4726e38/contracts/19ae67e-Specific_Conditions_-_BYOIP-FR-1.0.pdf'},
    {'key': '7', 'text': 'Premium Support', 'url': 'https://contract.eu.ovhapis.com/1.0/pdf/conditions_particulieres_support_premium-fr.pdf'},
    {'key': '8', 'text': 'Business Support', 'url': 'https://storage.gra.cloud.ovh.net/v1/AUTH_325716a587c64897acbef9a4a4726e38/contracts/646f900-Support_Business-FR-1.0.pdf'},
    {'key': '9', 'text': 'Entreprise Support', 'url': 'https://storage.gra.cloud.ovh.net/v1/AUTH_325716a587c64897acbef9a4a4726e38/contracts/6447221-Support_Entreprise-FR-1.0.pdf'},
    {'key': 'a', 'text': 'UGAP', 'url': ''},
    {'key': 'b', 'text': 'SNC', 'url': ''},
]

def get_legal():
    langs = ['fr', 'en']
    lang = langs[0]
    html = get_html(f'https://www.ovhcloud.com/{lang}/terms-and-conditions/contracts/')
    soup = bs4.BeautifulSoup(html, 'lxml')
    tr = soup.css.select('table tr')
    print(len(tr))



if __name__ == '__main__':
    get_legal()