from baremetal import baremetal
from privatecloud import privatecloud
from publiccloud import publiccloud
from utils import *
from support import get_support_prices
import datetime
import json
import gzip
import bs4
import unicodedata
from legal import get_legal_forward_links, OVH_SUBSIDIARY_ADDRESS

def save_indexes():
    dcs = get_dcs()
    print(*dict.values(dcs), sep='\n')
    assert len(dict.values(dcs)) >= 14

    print('Getting Baremetal Catalog')
    bm = exponential_backoff(baremetal)
    print('Getting Private Cloud Catalog')
    pcc = exponential_backoff(privatecloud)
    print('Getting Public Cloud Catalog')
    pci = exponential_backoff(publiccloud)
    supports = get_support_prices();

    version = 0
    # try:
    #     last_index = s3().get_object(Bucket=S3_BUCKET, Key=f'pricelist-index.json')
    #     last_index_content = json.loads(gzip.decompress(last_index['Body'].read()))
    #     print(f"Found index version: {last_index_content['version']}")
    #     version = last_index_content['version'] + 1
    # except boto3.resource('s3').meta.client.exceptions.NoSuchKey:
    #     pass
    data = {
        'version': version,
        'date': datetime.datetime.now().isoformat(),
        'dcs': dcs,
        'legal': get_legal_forward_links(),
        'addresses': OVH_SUBSIDIARY_ADDRESS,
        'subsidiaries': {},
    }
    for sub in SUBSIDIARIES:
        data['subsidiaries'][sub] = {}
        data['subsidiaries'][sub]['catalog'] = index_catalog(bm[sub]['catalog'], ENCODING_PREFIXES['bm']) | \
            index_catalog(pcc[sub]['catalog'], ENCODING_PREFIXES['pcc']) | \
            index_catalog(pci[sub]['catalog'], ENCODING_PREFIXES['pci'])
        data['subsidiaries'][sub]['locale'] = pcc[sub]['locale']
        data['subsidiaries'][sub]['support'] = supports[sub]

    json.dump(data, open('pricelist-index.json', 'w+'))
    upload_gzip_json(data, f'pricelist-index.json', S3_BUCKET)
    upload_gzip_json(data, f'pricelist-index-v{version}.json', S3_BUCKET)

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
        dcs[code] = {'code': code, 'city': dcs[tz]['city'] + ' (Trusted Zone)', 'country': dcs[tz]['country'] }

    assert len(dict.values(dcs)) > 13
    return dcs

if __name__ == '__main__':
    save_indexes()
