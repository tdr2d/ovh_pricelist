from baremetal import baremetal
from privatecloud import privatecloud
from publiccloud import publiccloud
from utils import *
import datetime
import json
import gzip
import bs4
import unicodedata

ENCODING_REGEXES = {
    'index_version': 'v([0-9]+)',
    'condition': 'c-',  # 'abcdefghij'
    'zone': 'z-([A-Z ]+)',
    'baremetal': 'b-',
    'privatecloud': 'q-',
    'publiccloud': 'p-',
    'commitment': 'e-',
    'discount': 'd-',
}
# format v-1c-abcdrfz-RBXq-adb-e-1d-0

def save_indexes(bm_indexes, pcc_indexes, pci_indexes, dcs):
    version = 0
    try:
        last_index = s3().get_object(Bucket=S3_BUCKET, Key=f'pricelist-index.json')
        last_index_content = json.loads(gzip.decompress(last_index['Body'].read()))
        print(f"Found index version: {last_index_content['version']}")
        version = last_index_content['version'] + 1
    except boto3.resource('s3').meta.client.exceptions.NoSuchKey:
        pass
    subs = {
        'version': version,
        'date': datetime.datetime.now().isoformat(),
        'dcs': dcs,
    }
    for sub in SUBSIDIARIES:
        subs[sub] = { 'b': bm_indexes[sub], 'q': pcc_indexes[sub], 'p': pci_indexes[sub] }

    upload_gzip_json(subs, f'pricelist-index.json')
    upload_gzip_json(subs, f'pricelist-index-v{version}.json')

def get_dcs():
    base_url = 'https://smokeping.ovh.net/smokeping'
    html = get_html(f'{base_url}?target=OVH.DCs')
    links = bs4.BeautifulSoup(html, 'lxml').css.select('ul.menuactive a.link')
    dcs = {}
    for link in links:
        txt = link.get_text()
        if 'IPv4' not in txt:
            continue
        country, code, _ = list(map(lambda x: x.strip(), unicodedata.normalize('NFKD', txt).split(' ')))
        title = bs4.BeautifulSoup(get_html(f'{base_url}{link.get("href")}'), 'lxml').head.title.get_text()
        city = title.split('OVH')[-1].strip()
        dcs[code] = {'city': city, 'code': code, 'country': country}
    
    for tz in TZ_DCS:
        code = f"{tz} TZ"
        dcs[code] = dcs[tz]
        dcs[code]['code'] = code
        dcs[code]['city'] += ' (Trusted Zone)'

    assert len(dict.values(dcs)) > 13
    return dcs

if __name__ == '__main__':
    dcs = get_dcs()
    print(*dict.values(dcs), sep='\n')

    print('Getting Baremetal Catalog')
    bm = exponential_backoff(baremetal)

    print('Getting Private Cloud Catalog')
    privatecloud_cat_idx = exponential_backoff(privatecloud)
    print('Getting Public Cloud Catalog')
    publiccloud_cat_idx = exponential_backoff(publiccloud)
    save_indexes(bm[1], privatecloud_cat_idx[1], publiccloud_cat_idx[1], dcs)
