from utils import *
from datetime import datetime
import pandas as pd

EXCLUDE_FAMILY = [
    'option-dc-adp',
    'ai-app',
    'ai-notebook',
    'ai-notebook-workspace',
    'ai-serving-engine',
    'ai-voxist',
    'bandwidth_instance',
    'data-integration',
    'data-processing-job',
    'data-processing-spark-notebook',
    'dataplatform',
    'publicip'
]

EXLUDE_PLAN_CODE = [
    'loadbalancer.loadbalancer-unit.hour.monthly.postpaid', # legacy lb
    'ai-training.ai1-standard.minute.monthly.postpaid',
    'ai-training.ai1-standard.hour.monthly.postpaid',
    'coldarchive.archive-fees.unit.consumption',
    'databases.mongodb-discovery-db2-free.month.consumption',
    'storage-standard.consumption.LZ',
    'storage-api-call.consumption',
    'storage-api-call_internal.consumption',
    'storage-standard.LZ.EU',
    'storage-standard.consumption.LZ.EU',
    'storage-standard-ia.consumption',
    'image.consumption.3AZ',
    'bandwidth_storage-standard_out.consumption.LZ.EU'
]

REPLACE_PRODUCT_MAP = {
    'bandwidth_archive_out consumption': 'Cloud Archive - Egress fees - per GB',
    'volume.snapshot': 'Volume Snapshot - per GB',
    'storage-high-perf': 'Object Storage High-Perf - per GB',
    'storage-standard-3AZ': 'Object Storage Standard-Perf 3AZ - per GB',
    'storage-standard': 'Object Storage Standard-Perf - per GB',
    'bandwidth_storage consumption': 'Outgoing public traffic (Egress) - per GB',
    'archive': 'Cloud Archive Storage - per GB',
    'image': 'Instance Backup - per GB',
    'archive consumption': 'Cloud Archive Storage - per GB',
}
MONTHLY_ONLY_FAMILIES = [
    'databases', 
    'gateway', 
    'loadbalancer', 
    'octavia-loadbalancer', 
    'volume', 
    'snapshot', 
    'registry',
    'floatingip',
    'volume-backup'
    # 'storage',
]

def instance_spec_string(x):
    if 'name' not in x['tech']:
        return ''
    ret = x['tech']['name']
    ret += f" {x['tech']['os']['family'].capitalize()} Instance"

    ret += f" {x['tech']['cpu']['cores']} vCores"
    ret += f", {x['tech']['memory']['size']} GB RAM"
    
    if 'gpu' in x['tech']:
        # "gpu": {"memory": {"interface": "HBM2", "size": 16}, "model": "Tesla V100", "number": 1},
        ret += f", {x['tech']['gpu']['number']}x GPU {x['tech']['gpu']['model']} {x['tech']['gpu']['memory']['size']} GB"

    ret += f", {storage_string(x['tech']['storage']['disks'][0]['capacity'])} {x['tech']['storage']['disks'][0]['technology'] if 'technology' in x['tech']['storage']['disks'][0] else ''}"
    if 'nvme' in x['tech']:
        # "nvme": {"disks": [{"capacity": 1900, "number": 2}]},
        ret += f", {x['tech']['nvme']['disks'][0]['number'] if 'number' in x['tech']['nvme']['disks'][0] else 1}x "
        ret += f"{storage_string(x['tech']['nvme']['disks'][0]['capacity'])} NVMe Disks"

    ret += f", {bandwidth_string(x['tech']['bandwidth']['level'])}{' guaranteed' if x['tech']['bandwidth']['guaranteed'] else ''} Public Bandwidth"
    ret += f", {bandwidth_string(x['tech']['vrack']['level'])}{' guaranteed' if x['tech']['vrack']['guaranteed'] else ''} Private Bandwidth"

    return ret

def bandwidth_string(mbps):
    if mbps < 1000:
        return f'{mbps} Mbps'
    return f'{int(mbps/1000) if (mbps/1000).is_integer() else mbps/1000} Gbps'

def storage_string(gb):
    if gb < 1000:
        return f'{gb} GB'
    val = round(gb/1000, 2)
    return f'{int(val) if val.is_integer() else val} TB'

def coldarchive_hotfix(item):
    if 'Cold Archive storage' in item['invoiceName']:
        item['duration'] = 'month'
        item['description'] = item['invoiceName'] + ' - per GB'
        item['price'] = item['price'] * 730
        item['plan_code'] = item['plan_code'].replace('hour','month')
    elif 'coldarchive.restore.unit.consumption' == item['plan_code']:
        item['description'] = 'Cold Archive restore' + ' - per GB'
    return item

def objectstorage_3az_hotfix(item):
    if item['plan_code'] == 'storage-standard-3AZ.consumption':
        item['duration'] = 'month'
        item['description'] = 'Object Storage Standard 3AZ - S3 API - per GB'
        item['price'] = item['price'] * 730
        item['family'] += '3az'
    return item

def index_addons(js):
    addon_per_plancode = {}
    for addon in js['addons']:
        addon_per_plancode[addon['planCode']] = addon
    return addon_per_plancode

def database_description(x):
    desc = x['invoiceName'].replace(' on region #REGION#', '').replace('Monthly usage for ', '').replace(' Public Cloud Databases', '')
    if ('-additional-storage-' in x['plan_code'] or '-additionnal-storage-' in x['plan_code']):
        return desc

    if 'brickSubtype' in x['com']:
        desc = f"{x['com']['brickSubtype']} - {x['com']['name']}"
    desc += f" 1x Node {x['tech']['cpu']['cores']} vCores, {x['tech']['memory']['size']} GB RAM"
    if 'storage' in x['tech']:
        desc += f" {storage_string(x['tech']['storage']['disks'][0]['maximumCapacity'])} Storage"
    return desc

# Map of family and function to render description
DESCRIPTION_RENDERERS = {
    'ai-training': lambda x: x['invoiceName'].replace(' on #REGION#', '').replace('Per minute usage for Public Cloud', '(Minute)').replace('Per hour usage for Public Cloud', '(Hourly)'),
    'databases': database_description,
    'floatingip': lambda x: x['com']['name'] if 'name' in x['com'] else x['invoiceName'],
    'gateway': lambda x: f"{x['com']['name']} - {bandwidth_string(x['tech']['bandwidth']['level'])}",
    'instance': instance_spec_string,
    'publiccloud-instance': instance_spec_string,
    'registry': lambda x: f"Managed Private Registry {x['com']['name']} - {storage_string(x['tech']['storage']['disks'][0]['capacity'])}",
    'snapshot': lambda x: 'Volume Backup - Stockage réplica x3 - per GB' if x['plan_code'] == 'snapshot.monthly.postpaid' else 'Volume Backup - Stockage réplica x3  - per GB',
    'storage': lambda x: {
        'archive': "Cloud Archive storage - per GB",
        'image': 'Instance Backup - per GB',
        'storage-standard': 'Object Storage Standard - S3 API - per GB',
        'storage-high-perf': 'Object Storage High Performance - S3 API - per GB',
        'storage': 'Object Storage Swift (legacy) - per GB',
    }[x['plan_code'].replace('.monthly.postpaid', '').replace('.consumption', '')] if 'bandwidth' not in x['plan_code'] else x['invoiceName'] + ' - per GB',
    'volume': lambda x: f"Block Storage - {x['tech']['name'].capitalize()} {x['tech']['volume']['iops']['level']} " + (f"{x['tech']['volume']['iops']['unit']} max {x['tech']['volume']['iops']['max']} IOPS" if 'unit' in x['tech']['volume']['iops'] else 'IOPS') + ' - per GB',
    'octavia-loadbalancer': lambda x: f"{x['invoiceName']} - {bandwidth_string(x['tech']['bandwidth']['level'])}"
}

# test : https://eu.api.ovh.com/v1/order/catalog/public/cloud?ovhSubsidiary=FR
def get_api_cloud_prices(sub, debug=False):
    url = f'{get_base_api(sub)}/1.0/order/catalog/public/cloud?ovhSubsidiary={sub}'
    print(url)
    cloud = get_json(url)
    addons_per_plancode = index_addons(cloud)
    families = next(filter(lambda x: x['planCode'] == 'project', cloud['plans']))['addonFamilies']
    currency = cloud['locale']['currencyCode']

    rows = []
    for family in families:
        if family['name'] in EXCLUDE_FAMILY:
            continue
        for planCode in family['addons']:
            if 'LZ.' in planCode or planCode in EXLUDE_PLAN_CODE:
                continue
            addon = addons_per_plancode[planCode]
            price = addon['pricings'][0]
            
            if int(price['price']) == 0 and float(price['price']).is_integer():
                continue
            

            duration = price['description'].lower()
            if 'month' in duration:
                duration = 'month'
            elif 'minute' in duration:
                duration = 'minute'
            elif 'hour' in duration or 'consumption' in duration:
                duration = 'hour'
            
            if addon['blobs'] and 'tags' in addon['blobs'] and ('legacy' in addon['blobs']['tags'] or ('coming_soon' in addon['blobs']['tags'] and 'active' not in addon['blobs']['tags'])):
                continue
            if duration != 'month' and family['name'] in MONTHLY_ONLY_FAMILIES:
                continue
            
            invoiceName = addon['invoiceName']
            blobs_commercial = addon['blobs']['commercial'] if addon['blobs'] and 'commercial' in addon['blobs'] else {}
            if 'price' in blobs_commercial:
                blobs_commercial.pop('price', None)
            blobs_technical = addon['blobs']['technical'] if addon['blobs'] and 'technical' in addon['blobs'] else {}

            item = {
                'family': family['name'],
                'invoiceName': invoiceName,
                'plan_code': planCode,
                'price': price['price'] / 100000000,
                'duration': duration
            }
            if not item['family']:
                print(item)

            if family['name'] == 'coldarchive':
                item = coldarchive_hotfix(item)
            if family['name'] == 'storage':
                item = objectstorage_3az_hotfix(item)

            if debug:
                print(item['plan_code'])
            #     print(blobs_commercial)
            #     print(blobs_technical)

            if item['family'] in DESCRIPTION_RENDERERS:
                item['description'] = DESCRIPTION_RENDERERS[family['name']]({'plan_code': planCode, 'invoiceName': invoiceName, 'com': blobs_commercial, 'tech': blobs_technical})
            elif 'description' not in item:
                item['description'] = invoiceName + json.dumps(blobs_commercial) + json.dumps(blobs_technical)
            rows.append(item)
    return { 'currency': currency, 'catalog': rows, 'date': datetime.now().isoformat() }


def publiccloud(debug=False):
    subs = {}
    debug = debug

    for sub in SUBSIDIARIES:
        publiccloud = get_api_cloud_prices(sub, debug=debug)
        df = pd.DataFrame(publiccloud['catalog'])
        df = df.drop_duplicates(subset=['plan_code', 'price'])
        df.update(df[df['duration'] == 'hour']['description'].apply(lambda x: ('(Hourly) ' if 'hour' not in x.lower() else '') + x))
        df.drop(['invoiceName'], axis=1, inplace=True)
        df = df[df.price != 0]
        catalog = df.to_dict('records')
        publiccloud['catalog'] = catalog
        subs[sub] = publiccloud

    upload_gzip_json(subs, f'public-cloud.json', S3_BUCKET)
    return subs

if __name__ == '__main__':
    publiccloud(debug=True)

