from utils import *
import requests

LEGALS = {
    'fr': {
        '0': {'text': 'General terms and conditions of services', 'url': 'https://contract.eu.ovhapis.com/1.0/pdf/contrat_genServices-fr.pdf'},
        '1': {'text': 'Baremetal', 'url': 'https://contract.eu.ovhapis.com/1.0/pdf/contrat_partDedie-fr.pdf'},
        '2': {'text': 'Private Cloud', 'url': 'https://contract.eu.ovhapis.com/1.0/pdf/HPCPremier-fr.pdf'},
        '3': {'text': 'Public Cloud', 'url': 'https://contract.eu.ovhapis.com/1.0/pdf/Conditions_particulieres_OVH_Stack-we.pdf'},
        '4': {'text': 'OVHCloud Connect', 'url': 'https://storage.gra.cloud.ovh.net/v1/AUTH_325716a587c64897acbef9a4a4726e38/contracts/efeb396-Contrat_part_OVHcloud_Connect-WE-2.0.pdf'},
        '5': {'text': 'Windows SPLA', 'url': 'https://storage.gra.cloud.ovh.net/v1/AUTH_325716a587c64897acbef9a4a4726e38/contracts/93af107-EULA_MCSFT_VPS_PCI-ALL-1.0.pdf'},
        '6': {'text': 'Bring Your Own IP (BYOIP)', 'url': 'https://storage.gra.cloud.ovh.net/v1/AUTH_325716a587c64897acbef9a4a4726e38/contracts/19ae67e-Specific_Conditions_-_BYOIP-FR-1.0.pdf'},
        '7': {'text': 'Premium Support', 'url': 'https://contract.eu.ovhapis.com/1.0/pdf/conditions_particulieres_support_premium-fr.pdf'},
        '8': {'text': 'Business Support', 'url': 'https://storage.gra.cloud.ovh.net/v1/AUTH_325716a587c64897acbef9a4a4726e38/contracts/646f900-Support_Business-FR-1.0.pdf'},
        '9': {'text': 'Entreprise Support', 'url': 'https://storage.gra.cloud.ovh.net/v1/AUTH_325716a587c64897acbef9a4a4726e38/contracts/6447221-Support_Entreprise-FR-1.0.pdf'},
        'a': {'text': 'UGAP', 'url': 'https://storage.gra.cloud.ovh.net/v1/AUTH_325716a587c64897acbef9a4a4726e38/contracts/51c2ad8-CGU_OVH_UGAP-FR-2.0.pdf'},
        'b': {'text': 'Private Cloud SNC', 'url': 'https://storage.gra.cloud.ovh.net/v1/AUTH_325716a587c64897acbef9a4a4726e38/contracts/eeb9b21-HPC_SNC-FR-2.1.pdf'},
        'c': {'text': 'Professional Service', 'url': 'https://storage.gra.cloud.ovh.net/v1/AUTH_325716a587c64897acbef9a4a4726e38/contracts/9eae50b-Contract_Professional_Services-FR-1.0.pdf'},
    },
    'en': {
        '0': {'text': 'General terms and conditions of services', 'url': 'https://contract.eu.ovhapis.com/1.0/pdf/contrat_genServices-ie.pdf'},
        '1': {'text': 'Baremetal', 'url': 'https://contract.eu.ovhapis.com/1.0/pdf/contrat_partDedie-ie.pdf'},
        '2': {'text': 'Private Cloud', 'url': 'https://contract.eu.ovhapis.com/1.0/pdf/HPCPremier-ie.pdf'},
        '3': {'text': 'Public Cloud', 'url': 'https://storage.gra.cloud.ovh.net/v1/AUTH_325716a587c64897acbef9a4a4726e38/contracts/7daede7-Conditions_particulieres_OVH_Stack-IE-16.0.pdf'},
        '4': {'text': 'OVHCloud Connect', 'url': 'https://storage.gra.cloud.ovh.net/v1/AUTH_325716a587c64897acbef9a4a4726e38/contracts/b23184e-Contrat_part_OVHcloud_Connect-IE-2.0.pdf'},
        '5': {'text': 'Windows SPLA', 'url': 'https://storage.gra.cloud.ovh.net/v1/AUTH_325716a587c64897acbef9a4a4726e38/contracts/93af107-EULA_MCSFT_VPS_PCI-ALL-1.0.pdf'},
        '6': {'text': 'Bring Your Own IP (BYOIP)', 'url': 'https://storage.gra.cloud.ovh.net/v1/AUTH_325716a587c64897acbef9a4a4726e38/contracts/3c533d7-Specific_Conditions_-_BYOIP-IE-1.0.pdf'},
        '7': {'text': 'Premium Support', 'url': 'https://contract.eu.ovhapis.com/1.0/pdf/conditions_particulieres_support_premium-ie.pdf'},
        '8': {'text': 'Business Support', 'url': 'https://storage.gra.cloud.ovh.net/v1/AUTH_325716a587c64897acbef9a4a4726e38/contracts/4803651-Support_Business-IE-1.0.pdf'},
        '9': {'text': 'Entreprise Support', 'url': 'https://storage.gra.cloud.ovh.net/v1/AUTH_325716a587c64897acbef9a4a4726e38/contracts/0c7221b-Support_Entreprise-IE-1.0.pdf'},
        'c': {'text': 'Professional Service', 'url': 'https://storage.gra.cloud.ovh.net/v1/AUTH_325716a587c64897acbef9a4a4726e38/contracts/d326065-Contract_Professional_Services-IE-1.0.pdf'},
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