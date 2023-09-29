from utils import *
import requests

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

LEGALS = {
    'fr': {
        '1': {'text': 'Baremetal', 'url': 'https://contract.eu.ovhapis.com/1.0/pdf/contrat_partDedie-fr.pdf'},
        '2': {'text': 'Private Cloud', 'url': 'https://contract.eu.ovhapis.com/1.0/pdf/HPCPremier-fr.pdf'},
        '3': {'text': 'Public Cloud', 'url': 'https://contract.eu.ovhapis.com/1.0/pdf/Conditions_particulieres_OVH_Stack-we.pdf'},
        '4': {'text': 'OVHCloud Connect', 'url': 'https://storage.gra.cloud.ovh.net/v1/AUTH_325716a587c64897acbef9a4a4726e38/contracts/efeb396-Contrat_part_OVHcloud_Connect-WE-2.0.pdf'},
        '5': {'text': 'EULA Windows', 'url': 'https://storage.gra.cloud.ovh.net/v1/AUTH_325716a587c64897acbef9a4a4726e38/contracts/93af107-EULA_MCSFT_VPS_PCI-ALL-1.0.pdf'},
        '6': {'text': 'Bring Your Own IP (BYOIP)', 'url': 'https://storage.gra.cloud.ovh.net/v1/AUTH_325716a587c64897acbef9a4a4726e38/contracts/19ae67e-Specific_Conditions_-_BYOIP-FR-1.0.pdf'},
        '7': {'text': 'Premium Support', 'url': 'https://contract.eu.ovhapis.com/1.0/pdf/conditions_particulieres_support_premium-fr.pdf'},
        '8': {'text': 'Business Support', 'url': 'https://storage.gra.cloud.ovh.net/v1/AUTH_325716a587c64897acbef9a4a4726e38/contracts/646f900-Support_Business-FR-1.0.pdf'},
        '9': {'text': 'Entreprise Support', 'url': 'https://storage.gra.cloud.ovh.net/v1/AUTH_325716a587c64897acbef9a4a4726e38/contracts/6447221-Support_Entreprise-FR-1.0.pdf'},
        'd': {'text': 'Support Editeur SNC ', 'url': 'https://storage.gra.cloud.ovh.net/v1/AUTH_325716a587c64897acbef9a4a4726e38/contracts/2cbc744-Support_Editeur_SNC-FR-2.0.pdf'},
        'a': {'text': 'UGAP', 'url': 'https://storage.gra.cloud.ovh.net/v1/AUTH_325716a587c64897acbef9a4a4726e38/contracts/51c2ad8-CGU_OVH_UGAP-FR-2.0.pdf'},
        'b': {'text': 'Private Cloud SNC', 'url': 'https://storage.gra.cloud.ovh.net/v1/AUTH_325716a587c64897acbef9a4a4726e38/contracts/eeb9b21-HPC_SNC-FR-2.1.pdf'},
        'c': {'text': 'Professional Service', 'url': 'https://storage.gra.cloud.ovh.net/v1/AUTH_325716a587c64897acbef9a4a4726e38/contracts/9eae50b-Contract_Professional_Services-FR-1.0.pdf'},
        'e': {'text': 'Adresses IP Additionnelles', 'url': 'https://storage.gra.cloud.ovh.net/v1/AUTH_325716a587c64897acbef9a4a4726e38/contracts/add4821-Contrat_part_IP-FR-2.0.pdf'},
    },
    'en': {
        '1': {'text': 'Baremetal', 'url': 'https://contract.eu.ovhapis.com/1.0/pdf/contrat_partDedie-ie.pdf'},
        '2': {'text': 'Private Cloud', 'url': 'https://contract.eu.ovhapis.com/1.0/pdf/HPCPremier-ie.pdf'},
        '3': {'text': 'Public Cloud', 'url': 'https://storage.gra.cloud.ovh.net/v1/AUTH_325716a587c64897acbef9a4a4726e38/contracts/7daede7-Conditions_particulieres_OVH_Stack-IE-16.0.pdf'},
        '4': {'text': 'OVHCloud Connect', 'url': 'https://storage.gra.cloud.ovh.net/v1/AUTH_325716a587c64897acbef9a4a4726e38/contracts/b23184e-Contrat_part_OVHcloud_Connect-IE-2.0.pdf'},
        '5': {'text': 'EULA Windows', 'url': 'https://storage.gra.cloud.ovh.net/v1/AUTH_325716a587c64897acbef9a4a4726e38/contracts/93af107-EULA_MCSFT_VPS_PCI-ALL-1.0.pdf'},
        '6': {'text': 'Bring Your Own IP (BYOIP)', 'url': 'https://storage.gra.cloud.ovh.net/v1/AUTH_325716a587c64897acbef9a4a4726e38/contracts/3c533d7-Specific_Conditions_-_BYOIP-IE-1.0.pdf'},
        '7': {'text': 'Premium Support', 'url': 'https://contract.eu.ovhapis.com/1.0/pdf/conditions_particulieres_support_premium-ie.pdf'},
        '8': {'text': 'Business Support', 'url': 'https://storage.gra.cloud.ovh.net/v1/AUTH_325716a587c64897acbef9a4a4726e38/contracts/4803651-Support_Business-IE-1.0.pdf'},
        '9': {'text': 'Entreprise Support', 'url': 'https://storage.gra.cloud.ovh.net/v1/AUTH_325716a587c64897acbef9a4a4726e38/contracts/0c7221b-Support_Entreprise-IE-1.0.pdf'},
        'd': {'text': 'Support Editeur SNC ', 'url': 'https://storage.gra.cloud.ovh.net/v1/AUTH_325716a587c64897acbef9a4a4726e38/contracts/2cbc744-Support_Editeur_SNC-FR-2.0.pdf'},
        'a': {'text': 'UGAP', 'url': 'https://storage.gra.cloud.ovh.net/v1/AUTH_325716a587c64897acbef9a4a4726e38/contracts/51c2ad8-CGU_OVH_UGAP-FR-2.0.pdf'},
        'b': {'text': 'Private Cloud SNC', 'url': 'https://storage.gra.cloud.ovh.net/v1/AUTH_325716a587c64897acbef9a4a4726e38/contracts/eeb9b21-HPC_SNC-FR-2.1.pdf'},
        'c': {'text': 'Professional Service', 'url': 'https://storage.gra.cloud.ovh.net/v1/AUTH_325716a587c64897acbef9a4a4726e38/contracts/d326065-Contract_Professional_Services-IE-1.0.pdf'},
        'e': {'text': 'Additional IP', 'url': 'https://storage.gra.cloud.ovh.net/v1/AUTH_325716a587c64897acbef9a4a4726e38/contracts/1e16312-Contrat_part_IP-IE-2.0.pdf'},
    },
    'de': {
        '1': {'text': 'Baremetal', 'url': 'https://contract.eu.ovhapis.com/1.0/pdf/contrat_partDedie-de.pdf'},
        '2': {'text': 'Private Cloud', 'url': 'https://contract.eu.ovhapis.com/1.0/pdf/HPCPremier-de.pdf'},
        '3': {'text': 'Public Cloud', 'url': 'https://storage.gra.cloud.ovh.net/v1/AUTH_325716a587c64897acbef9a4a4726e38/contracts/db5c164-Conditions_particulieres_OVH_Stack-DE-17.0.pdf'},
        '4': {'text': 'OVHCloud Connect', 'url': 'https://storage.gra.cloud.ovh.net/v1/AUTH_325716a587c64897acbef9a4a4726e38/contracts/adf8390-Contrat_part_OVHcloud_Connect-DE-2.0.pdf'},
        '5': {'text': 'EULA Windows', 'url': 'https://storage.gra.cloud.ovh.net/v1/AUTH_325716a587c64897acbef9a4a4726e38/contracts/93af107-EULA_MCSFT_VPS_PCI-ALL-1.0.pdf'},
        '6': {'text': 'Bring Your Own IP (BYOIP)', 'url': 'https://storage.gra.cloud.ovh.net/v1/AUTH_325716a587c64897acbef9a4a4726e38/contracts/01606c1-Specific_Conditions_-_BYOIP-DE-1.0.pdf'},
        '7': {'text': 'Premium Support', 'url': 'https://contract.eu.ovhapis.com/1.0/pdf/conditions_particulieres_support_premium-de.pdf'},
        '8': {'text': 'Business Support', 'url': 'https://storage.gra.cloud.ovh.net/v1/AUTH_325716a587c64897acbef9a4a4726e38/contracts/25f3e90-Support_Business-DE-1.0.pdf'},
        '9': {'text': 'Entreprise Support', 'url': 'https://storage.gra.cloud.ovh.net/v1/AUTH_325716a587c64897acbef9a4a4726e38/contracts/7888141-Support_Entreprise-DE-1.0.pdf'},
        'd': {'text': 'Support Editeur SNC ', 'url': 'https://storage.gra.cloud.ovh.net/v1/AUTH_325716a587c64897acbef9a4a4726e38/contracts/2cbc744-Support_Editeur_SNC-FR-2.0.pdf'},
        'a': {'text': 'UGAP', 'url': 'https://storage.gra.cloud.ovh.net/v1/AUTH_325716a587c64897acbef9a4a4726e38/contracts/51c2ad8-CGU_OVH_UGAP-FR-2.0.pdf'},
        'b': {'text': 'Private Cloud SNC', 'url': 'https://storage.gra.cloud.ovh.net/v1/AUTH_325716a587c64897acbef9a4a4726e38/contracts/eeb9b21-HPC_SNC-FR-2.1.pdf'},
        'c': {'text': 'Professional Service', 'url': 'https://storage.gra.cloud.ovh.net/v1/AUTH_325716a587c64897acbef9a4a4726e38/contracts/d326065-Contract_Professional_Services-IE-1.0.pdf'},
        'e': {'text': 'Additional IP', 'url': 'https://storage.gra.cloud.ovh.net/v1/AUTH_325716a587c64897acbef9a4a4726e38/contracts/ded543d-Contrat_part_IP-DE-2.0.pdf'},
    },
}

def get_legal_forward_links():
    print('Getting legal links')
    for lang in dict.keys(LEGALS):
        for key in dict.keys(LEGALS[lang]):
            r = requests.get(LEGALS[lang][key]['url'], timeout=10)
            LEGALS[lang][key]['url'] = r.url
    return LEGALS


if __name__ == '__main__':
    get_legal_forward_links()