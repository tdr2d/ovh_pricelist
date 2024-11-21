from utils import *
from datetime import datetime
import pandas as pd
import bs4
import re

EXCLUDE_FAMILY = [
    'option-dc-adp',
    'ai-app',
    'ai-notebook',
    'ai-notebook-workspace',
    'ai-serving-engine',
    'ai-voxist',
    'bandwidth_instance',
    'data-integration'
]
EXCLUDE_PRODUCTS = [
    'bandwidth_archive_out',
    'bandwidth_storage',
    'serco-asp-r2-256 monthly instance', 'serco-asp-r2-256'
    'eg-120', 'win-eg-120',
    'eg-15', 'win-eg-15',
    'eg-30', 'win-eg-30',
    'eg-60', 'win-eg-60',
    'eg-7', 'win-eg-7',
    'g1-15', 'win-g1-15',
    'g1-30', 'win-g1-30',
    'g2-15', 'win-g2-15',
    'g2-30', 'win-g2-30',
    'g3-120', 'win-g3-120',
    'g3-30', 'win-g3-30',
    'hg-120', 'win-hg-120',
    'hg-15', 'win-hg-15',
    'hg-30', 'win-hg-30',
    'hg-60', 'win-hg-60',
    'hg-7', 'win-hg-7',
    's1-2', 'win-s1-2', 
    's1-4', 'win-s1-4', 
    's1-8', 'win-s1-8', 
    'sp-120', 'win-sp-120', 
    'sp-240', 'win-sp-240', 
    'sp-30', 'win-sp-30', 
    'sp-60', 'win-sp-60', 
    'vps-ssd-1', 'win-vps-ssd-1', 
    'vps-ssd-2', 'win-vps-ssd-2', 
    'vps-ssd-3', 'win-vps-ssd-3',
    'ks-1',
    'ks-2',
]
REPLACE_PRODUCT_MAP = {
    'bandwidth_archive_out consumption': 'Cloud Archive - Egress fees - per GB',
    'volume.snapshot': 'Volume Snapshot - per GB',
    'storage-high-perf': 'Object Storage High-Perf - per GB',
    'storage-standard': 'Object Storage Standard-Perf - per GB',
    'storage-standard': 'Object Storage Standard-Perf - per GB',
    'bandwidth_storage consumption': 'Outgoing public traffic (Egress) - per GB',
    'archive': 'Cloud Archive Storage - per GB',
    'image': 'Instance Backup - per GB',
    'archive consumption': 'Cloud Archive Storage - per GB',
}
MONTHLY_ONLY_FAMILIES = ['databases', 'gateway', 'loadbalancer', 'octavia-loadbalancer', 'volume', 'snapshot', 'registry']
def get_api_cloud_prices(sub, debug=False):
    url = f'{get_base_api(sub)}/1.0/order/catalog/formatted/cloud?ovhSubsidiary={sub}'
    print(url)
    cloud = get_json(url)
    families = next(filter(lambda x: x['planCode'] == 'project', cloud['plans']))['addonsFamily']
    currency = cloud['plans'][0]['details']['pricings']['default'][0]['price']['currencyCode']

    rows = []
    for family in families:
        if family['family'] in EXCLUDE_FAMILY:
            continue
        for addon in family['addons']:
            planCode = addon['plan']['planCode']
            if 'LZ.AF' in planCode:
                continue

            for price in addon['plan']['details']['pricings']['default']:
                duration = price['description'].lower()
                invoiceName = addon['plan']['invoiceName'] if family['family'] == 'ai-training' else addon['invoiceName']
                invoiceName = invoiceName.replace(' on region #REGION#', '').replace(' on #REGION#', '')
                invoiceName = invoiceName.replace('Monthly usage for ', '')
                invoiceName = invoiceName.replace('Public Cloud Database', '').strip()


                if invoiceName in EXCLUDE_PRODUCTS or invoiceName.replace(' consumption', '').strip() in EXCLUDE_PRODUCTS:
                    continue
                

                if 'month' in duration:
                    duration = 'month'
                elif 'minute' in duration:
                    duration = 'minute'
                elif 'hour' in duration or 'consumption' in duration:
                    duration = 'hour'

                invoiceName = re.sub(r'^snapshot$', 'Volume Backup - per GB',  invoiceName)
                invoiceName = re.sub(r'^storage$', 'Object Storage Swift - per GB',  invoiceName)
                for token in dict.keys(REPLACE_PRODUCT_MAP):
                    invoiceName = invoiceName.replace(token, REPLACE_PRODUCT_MAP[token])
                if family['family'] == 'coldarchive':
                    invoiceName = invoiceName + ' - per GB'

                

                item = {
                    'family': family['family'],
                    'invoiceName': invoiceName,
                    'key': invoiceName.lower()
                        .replace('octavia ', '')
                        .replace('large','l')
                        .replace('small', 's')
                        .replace('medium','m')
                        .replace(' - ', '-')
                        .replace('plan mensuel ', '')
                        .replace('pour ', '')
                        .replace(' unit', '')
                        .replace('public cloud ', '')
                        .replace('-plan-equivalent', '').strip(),
                    'price': price['price']['value'],
                    'duration': duration
                }
                if debug and invoiceName:
                    print(f'planCode: {planCode}\tInvoiceName: {invoiceName.lower()}\tkey: {item["key"]}\tprice:{item["price"]}')
                if item['price'] < 0.00000001 or ('hour' in duration and item['family'] in MONTHLY_ONLY_FAMILIES):
                    continue
                if family['family'] == 'instance':
                    item['key'] = item['key'].replace(' consumption', '')
                if family['family'] == 'databases':
                    item['key'] = item['key'].replace('apache ', '')
                rows.append(item)
    return { 'currency': currency, 'catalog': rows, 'date': datetime.now().isoformat() }


COLUMNS_RENAME = {
    'Dedicated node(s)': 'node(s)',
    'Memory': 'RAM',
    'Usable storage': 'SSD',
    'vCore': 'vCPU'
}
def merge_columns(columns):
    merged_cols = []
    for cols in columns:
        if isinstance(cols, str) or len(cols) == 1:
            merged_cols = list(columns)
            break
        if 'unnamed' in cols[0].lower() or 'informations' in cols[0].lower():
            merged_cols.append(cols[1])
        else:
            merged_cols.append(cols[0])
    
    for i in range(len(merged_cols)):
        if merged_cols[i] in COLUMNS_RENAME:
            merged_cols[i] = COLUMNS_RENAME[merged_cols[i]]
    return merged_cols


def webpage_build_key_description(df, family, title):
    keys, descriptions = [], []
    for i, row in df.iterrows():
        desc = title.strip() + ' '
        key = ''
        if family == 'compute':
            desc = 'Linux Instance '
        elif family == 'network':
            desc = ''

        for i in range(len(df.columns)):
            col = df.columns[i]
            if pd.isna(row[col]) or '_' == row[col]:
                continue
        
            if col == 'Name':
                name = row['Name'].strip()
                key = name.lower()
                if 'win-' in name:
                    desc = desc.replace('Linux', 'Windows')
                    name = name.replace('win-', '')

                desc += f"{name} -"
                if family == 'databases':
                    key = f'{title} {name}'.lower().replace('™', '')
                elif title == 'Managed Private Registry':
                    key = 'registry.' + key
                continue
            elif family == 'storage' and 'volume' in col.lower(): # Volume Block Storage
                key = f'volume.{row[col].replace("Volume","").strip().replace(" ", "-")}'

            if family == 'databases' and col == 'SSD':
                ret = re.findall(r'From (.*?) to.+', row[col])
                desc += ' ' + ret[0] if bool(ret) else row[col] + f" {col},"
            else:
                desc += f" {row[col]} {col},"

        desc = re.sub(r'\s\s+', ' ', desc)[:-1].strip()
        if family == 'storage' and 'per GB' not in desc:
            desc += ' - per GB'

        keys.append(key.lower().replace('load balancer ', 'loadbalancer-').replace('load balancer', 'loadbalancer'))
        descriptions.append(desc)
    return keys, descriptions

def get_webpage(debug=False):
    html = get_html('https://www.ovhcloud.com/en/public-cloud/prices/#')
    soup = bs4.BeautifulSoup(html, 'lxml')
    container = soup.css.select('#compute')[0].parent
    family, title, = '', ''
    keys, descriptions = [], []
    for div in container.find_all('div', recursive=False):
        if div.get('id'):
            family = div.get('id').strip()

        h3s = div.css.select('h3.public-cloud-prices-title')
        if bool(h3s):
            title = h3s[0].get_text().strip()

            try:
                dfs = pd.read_html(str(div))
                if 'mongo' in title.lower() and len(dfs) > 1: # remove the different free tier which have only 1 dimentional columns
                    dfs = dfs[1:]
                df = pd.concat(dfs)
                df.columns = merge_columns(df.columns)
                for col_to_drop in ['Price', 'Total price']:
                    if col_to_drop in df.columns:
                        df.drop(col_to_drop, axis=1, inplace=True)

                if family == 'compute':
                    win_df = df.copy()
                    win_df['Name'] = win_df['Name'].apply(lambda x: 'win-' + x)
                    df = pd.concat([df, win_df])
                
                k, d = webpage_build_key_description(df, family, title)
                keys += k
                descriptions += d
            except ValueError:
                pass
    if debug:
        print(*filter(None, keys), sep='\n')
    return pd.DataFrame(zip(keys, descriptions), columns=['key', 'description'])

def publiccloud():
    subs = {}
    debug = False
    if debug:
        print('********************************** WEBPAGE KEYS **********************************')
    df_desc = get_webpage(debug=debug)
    if debug:
        print('********************************** API KEYS **********************************')

    for sub in SUBSIDIARIES:
        publiccloud = get_api_cloud_prices(sub, debug=debug)
        df_agora = pd.DataFrame(publiccloud['catalog'])
        df = pd.merge(df_agora, df_desc, how='left', on='key')
        df['description'] = df['description'].combine_first(df['invoiceName'])
        df = df.drop_duplicates(subset=['invoiceName', 'price'])
        df.update(df[df['duration'] == 'hour']['description'].apply(lambda x: ('(Hourly) ' if 'hour' not in x.lower() else '') + x))

        df.drop(['invoiceName', 'key'], axis=1, inplace=True)
        catalog = df.to_dict('records')
        publiccloud['catalog'] = catalog
        subs[sub] = publiccloud

    upload_gzip_json(subs, f'public-cloud.json', S3_BUCKET)
    return subs

if __name__ == '__main__':
    publiccloud()

