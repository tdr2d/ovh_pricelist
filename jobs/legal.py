from utils import *
import requests
import bs4
import json


OVH_SUBSIDIARY_ADDRESS = {
    'FR': 'OVHCloud - 2 rue Kellermann BP 80 157 59053 Roubaix Cedex 1 – France Société par Actions Simplifiée au capital de 10 174 560 € - RCS Lille Métropole 424 761 419 – Code APE 2620Z N°TVA FR22424761419',
    'CZ': '',
    'DE': 'OVH GmbH, with an authorized capital of € 25.000,  having its registered offfice at  Christophstraße 19, 50670 Köln, Germany registered in Commercial Register Saarbrücken, with the Company Registration Number HRB 15369, USt-IdNr.: DE245768940',
    'ES': 'OVH HISPANO SL, with an authorised capital of € 203 006 having its registered offfice at C/ Alcalá 21, 5.ª planta, 28014 Madrid, España, registered in the Registro Mercantil de Madrid Tomo 19.514, Folio 77, Sección 8ª, Hoja M-342678 e inscripción 5ª',
    'FI': '',
    'CA': 'HEBERGEMENT OVH INC., société par actions régie par la Loi sur les sociétés par actions (RLRQ, C. S-31.1), dont le siège social est situé au 800-1801 avenue McGill Collège, Montréal, QC, H3A 2N4 (Canada)',
    'IE': 'OVH Hosting Limited, registered under number 468585, with its offices at 38/39 Fitzwilliam Square West Dublin 2 D02 NX53 , Ireland',
    'IT': 'OVH srl, with an authorized capital of € 200 000,  having its registered offfice at  Via Carlo Imbonati, 18 20159, Italy registered in Camera di Commercio della Provincia di Milano, Lodi, Monza e Brianza, with the Company Registration Number ID 06157670966',
    'LT': '',
    'MA': '',
    'NL': '',
    'PL': 'OVH Spółka z ograniczoną odpowiedzialnością z siedzibą we Wrocławiu (50-088), przy ul. Swobodna 1, wpisaną do Rejestru Przedsiębiorców KRS prowadzonego przez Sąd Rejonowy dla Wrocławia – Fabrycznej we Wrocławiu, VI Wydział Gospodarczy Krajowego Rejestru Sądowego pod numerem KRS: 0000220286, NIP: 8992520556, REGON: 933029040, kapitał zakładowy w wysokości 50.000,00 zł.',
    'PT': 'OVH HOSTING - SISTEMAS INFORMÁTICOS, UNIPESSOAL LDA with an authorised capital of € 10.000,00,having its registered offfice at Praça de Alvalade, nº 7, 7º dtº 1700 036 Lisboa, Portugal, registered in CRComercial Lisboa with the Company Registration Number ID508769329',
    'SN': '',
    'TN': '',
    'US': '',
    'GB': 'OVH Limited , headquartered at Becket House, 1 Lambeth Palace Road, London SE1 7EU and registered under number 05519821',
}

LEGALS_DATA = {
    'fr': {
        'link': 'https://www.ovhcloud.com/fr/terms-and-conditions/contracts/',
        'mandatory_keys' :[
            {'key': "Conditions générales de service" },
            {'key': "Annexe Traitement de données à caractère personnel" },
        ],
        'to_select_keys' : [
            {'key': "Conditions particulières du service OVH Public Cloud", 'selected': True },
            {'key': "Conditions Particulieres Hosted Private Cloud VMware on OVHcloud", 'selected': True },
            {'key': "Conditions particulières de location de serveurs dédiés", 'selected': True },
            {'key': "Conditions particulieres Support Premium", 'selected': False },
            {'key': "Conditions particulières Support Business", 'selected': True },
            {'key': "Conditions particulières Support Entreprise", 'selected': True },
            {'key': "Conditions Particulières SAP HANA on Private Cloud", 'selected': False },
            {'key': "Conditions particulières OVHcloud Connect", 'selected': False },
            {'key': "Conditions Particulières Load Balancer", 'selected': False },
            {'key': "Conditions Générales de Services Professionnels", 'selected': True },
            {'key': None, 'title': "HDS pour VMware on OVHcloud - Serveurs Dédiés - Nutanix - File Storage", 'selected': False, 'url': "https://contract.eu.ovhapis.com/1.0/pdf/HPC_HDS-fr.pdf" },
            {'key': None, 'title': "Healthcare - Public Cloud", 'selected': False, 'url': "https://contract.eu.ovhapis.com/1.0/pdf/Public_Cloud_Health_Care_HDS-fr.pdf" },
            {'key': None, 'title': 'Conditions Particulières HPC SNC', 'selected': False, 'url': 'https://storage.gra.cloud.ovh.net/v1/AUTH_325716a587c64897acbef9a4a4726e38/contracts/0c59e05-HPC_SNC-FR-3.0.pdf '},
            {'key': None, 'title': "Conditions Particulières Support Editeur d'OVHcloud pour HPC SecNumCloud", 'selected': False, 'url': 'https://storage.gra.cloud.ovh.net/v1/AUTH_325716a587c64897acbef9a4a4726e38/contracts/2cbc744-Support_Editeur_SNC-FR-2.0.pdf'}
        ]
    },
    'en': {
        'link': 'https://www.ovhcloud.com/en-ie/terms-and-conditions/contracts/',
        'mandatory_keys' :[
            {'key': "General terms and conditions of services" },
            {'key': "Data Processing Agreement"}
        ],
        'to_select_keys' : [
            {'key': "Specific Conditions for Public Cloud", 'selected': True},
            {'key': "Specific Conditions Hosted Private Cloud VMware on OVHcloud", 'selected': True},
            {'key': None, 'title': "Specific Conditions for Baremetal Servers", 'selected': True, 'url': 'https://contract.eu.ovhapis.com/1.0/pdf/contrat_partDedie-ie.pdf'},
            {'key': "OVH Premium Support Specific Conditions", 'selected': False},
            {'key': "Specific Conditions OVHcloud Business Support", 'selected': True},
            {'key': "Specific Conditions OVHcloud Enterprise Support", 'selected': True},
            {'key': "Specific Conditions - SAP HANA on Private Cloud", 'selected': True},
            {'key': "Specific Conditions - Professional Services", 'selected': True},
            {'key': "Specific Conditions OVHcloud Connect", 'selected': False},
            {'key': "Specific Conditions for Load Balancer", 'selected': False},
        ]
    },
    'de': {
        'link': 'https://www.ovhcloud.com/de/terms-and-conditions/contracts/',
        'mandatory_keys' :[
            {'key': "AGB"},
            {'key': "Auftragsverarbeitungsvertrag 2018", 'title': 'Auftragsverarbeitungsvertrag'},
        ],
        'to_select_keys' : [
            {'key': "BESONDERE VERTRAGSBEDINGUNGEN FÜR PUBLIC-CLOUD-DIENSTE", 'selected': True},
            {'key': "Specific Conditions Hosted Private Cloud VMware on OVHcloud", 'selected': True},
            {'key': "Anlage DRS (dedizierte Rootserver)", 'selected': True},
            {'key': "BedingungenOVH Premium Support", 'selected': False},
            {'key': "Besondere Bedingungen OVHcloud Business Support", 'selected': True},
            {'key': "Besondere Bedingungen OVHcloud Enterprise Support", 'selected': True},
            {'key': "Besondere Vertragsbedingungen Sap Hana on Private Cloud", 'selected': False},
            {'key': "Besondere Vertragsbedingungen - Professional Services", 'selected': True},
            {'key': "Besondere Vertragsbedingungen - OVHcloud Connect", 'selected': False},
            {'key': "Besondere Vertragsbedingungen Load Balancer", 'selected': False},
        ]
    }
}


def get_all_legal_terms():
    print('Getting legal terms')
    for lang in dict.keys(LEGALS_DATA):
        legal_terms_map = get_legal_terms_map(lang)

        for item in LEGALS_DATA[lang]['mandatory_keys'] + LEGALS_DATA[lang]['to_select_keys']:
            if item['key'] is not None:
                assert item['key'] in legal_terms_map, f"Missing terms \"{item['key']}\" in website {LEGALS_DATA[lang]['link']}"
                url = legal_terms_map[item['key']]
            else:
                url = item['url']
            item['url'] = get_forward_link(url)
    return LEGALS_DATA

def get_forward_link(url, timeout=10):
    r = requests.get(url, timeout=timeout)
    return r.url

def print_keys():
    for lang in dict.keys(LEGALS_DATA):
        print(f"Country: {lang}, url: {LEGALS_DATA[lang]['link']}")
        legal_terms_map = get_legal_terms_map(lang)
        print(*dict.keys(legal_terms_map), sep='\n')
        print('')

# Get the map title > url
def get_legal_terms_map(lang):
    r = requests.get(LEGALS_DATA[lang]['link'])
    r.encoding = r.apparent_encoding
    html = r.text
    soup = bs4.BeautifulSoup(html, 'html.parser')
    links = soup.select('.ods-table-standard [data-tc-clic]')
    link_map = {}
    for link in links:
        title = link['title'].strip()
        link_map[title] = link['href'].strip()
    return link_map

if __name__ == '__main__':
    # get_legal_forward_links()
    # print_keys()
    legal_terms = get_all_legal_terms()
    print(json.dumps(legal_terms, ensure_ascii=False, indent=2))