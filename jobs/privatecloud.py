from utils import *
import re
from datetime import datetime
import pandas as pd
from copy import deepcopy
import numpy as np

CONFORMITY = ['default', 'hds', 'hipaa', 'pcidss'] # snc computed
RANGES = ['vsphere', 'essentials', 'nsx-t']
SNC_RANGES = ['vsphere', 'nsx-t']
SNC_PRODUCTS = [
    {'range': '', 'type': 'SNC Network', 'description': 'SNC VPN Gateway, 2x1 Gbps (Max 2x10 tunnels)', 'price_snc': round(400*SNC_MARKUP)},
    {'range': '', 'type': 'SNC Network', 'description': 'SNC VPN Gateway, 2x2 Gbps (Max 2x10 tunnels)', 'price_snc': round(800*SNC_MARKUP)},
    {'range': '', 'type': 'SNC Network', 'description': 'SNC VPN Gateway, 2x5 Gbps (Max 2x10 tunnels)', 'price_snc': round(1800*SNC_MARKUP)},
    {'range': '', 'type': 'SNC Network', 'description': 'SNC VPN Gateway, 2x10 Gbps (Max 2x10 tunnels)', 'price_snc': round(3400*SNC_MARKUP)},
    {'range': '', 'type': 'SNC Network', 'description': 'SNC SPN (Secured Private Network) incluant:\n   - 5 SPNs\n - 5 sous-réseaux par SPN\n - 50 routes statiques par SPN\n - Trafic illimité', 'price_snc': round(1000*SNC_MARKUP)},
    {'range': '', 'type': 'SNC Network', 'description': 'SNC SPN option connectivité InterDC chiffré\n  - Trafic illimité', 'price_snc': round(1000*SNC_MARKUP)},
]
TZ_REGION = ['RBX_TZ', 'SBG_TZ']
SNC_PS_PRICE = 2000
STORAGE_PACK_DESCRIPTION = '2x Datastore 3 TB'
BACKUP_DESCRIPTION = {
    'classic': 'Veeam Managed Backup - Standard',
    'advanced': 'Veeam Managed Backup - Advanced', 
    'premium': 'Veeam Managed Backup - Premium',
}
BACKUP_SIZE = {
    's': 'Max 250 GB per VM',
    'm': 'Max 1 TB per VM',
    'l': 'Max 2 TB per VM',
}

def get_addon_families(obj):
    plan_codes = {}
    for addonFamily in obj['addonsFamily']:
        for addon in addonFamily['addons']:
            if 'addonsFamily' in addon['plan']:
                plan_codes = plan_codes | get_addon_families(addon['plan'])
            
            item = {
                'family': addonFamily['family'],
                'invoiceName': addon['invoiceName'],
            }
            for pricing_key in addon['plan']['details']['pricings']:
                conformity = pricing_key.split('-')[-1] 
                if conformity not in CONFORMITY:
                    continue
                
                for pricing in addon['plan']['details']['pricings'][pricing_key]:
                    item[f"price_{conformity}"] = pricing['price']['value']
            
            if item['price_default'] > 0 and 'hourly' not in item['family']:
                if '_eu' in addon['plan']['planCode'] and addon['plan']['planCode'].replace('_eu', '') not in plan_codes:
                    plan_codes[addon['plan']['planCode'].replace('_eu', '')] = item
                plan_codes[addon['plan']['planCode']] = item
    return plan_codes

def get_backup_options(pcc_plan_codes):
    managed_backup = list(filter(lambda x: 'backup' in x['family'] and 'legacy' not in x['invoiceName'], dict.values(pcc_plan_codes)))
    for m in managed_backup:
        size, plan = m['invoiceName'].split('-')[-1], m['invoiceName'].split('-')[-2]
        m['description'] = f"{BACKUP_DESCRIPTION[plan]} - {BACKUP_SIZE[size]}"
        m['type'] = 'Managed Backups'
    return managed_backup

def get_occ_options(sub='FR'):
    occ = get_json(f'{get_base_api(sub)}/1.0/order/catalog/public/ovhCloudConnect?ovhSubsidiary={sub}')
    plans = []
    if 'plans' not in occ:
        return []
    for plan in occ['plans']:
        installPlan = list(filter(lambda x: x['description'] == "Frais d'installation", plan['pricings']))
        mPlan = map(lambda x: x['price'], filter(lambda x: x['description'] != "Frais d'installation", plan['pricings']))
        mPlan = sorted(list(mPlan))

        price = mPlan[-1] / 10**8
        assert price > 0
        item = { 'description': plan['invoiceName'], 'setupfee': installPlan[0]['price'] / 10**8 if installPlan else 0, 'type': 'OCC' }
        for con in CONFORMITY + ['snc']:
            item['price_'+con] = price
        plans.append(item)
    return plans

def get_ip_lb(sub='FR'):
    try:
        lbs = get_json(f'{get_base_api(sub)}/1.0/order/catalog/public/ipLoadbalancing?ovhSubsidiary={sub}')
    except urllib.error.HTTPError: # 404
        return []
    plans = []

    for plan in lbs['addons']:
        mPlan = map(lambda x: x['price'], filter(lambda x: 'installation' not in x['description'].lower(), plan['pricings']))
        mPlan = sorted(list(mPlan))

        price = mPlan[-1]

        desc = 'Certificates'
        if 'lb1' in plan['planCode']:
            desc = 'IP LB - Pack 1'
        elif 'lb2' in plan['planCode']:
            desc = 'IP LB - Pack 2'
        elif 'dedicated' in plan['planCode']:
            desc = 'IP LB - Dedicated'
        assert price > 0

        if 'consumption' in plan['invoiceName']:
            continue
        item = {'type': 'IP LB', 'description': desc + ' - ' + plan['invoiceName'].split(' zone')[0].strip()}
        for con in CONFORMITY + ['snc']:
            item['price_'+con] = price / 10 ** 8
        plans.append(item)
    return plans

def get_ps(sub='FR'):
    try:
        ps = get_json(f'{get_base_api(sub)}/1.0/order/catalog/public/packsProfessionalServices?ovhSubsidiary={sub}')
    except urllib.error.HTTPError: # 404
        return []
    plans = []
    for plan in ps['plans']:
        mPlan = map(lambda x: x['price'], filter(lambda x: 'installation' not in x['description'].lower(), plan['pricings']))
        mPlan = sorted(list(mPlan))
        price = mPlan[-1]
        item = {'type': 'PS', 'description': plan['invoiceName'], 'setupfee': price / 10 ** 8}
        for con in CONFORMITY + ['snc']:
            item['price_'+con] = 0
        plans.append(item)
        plans.append({'type': 'PS', 'description': plan['invoiceName'], 'setupfee': price / 10 ** 8, 'price_snc': 0})
    return plans

def parse_windows_licenses(plan_codes, list_of_cores):
    plans = filter(lambda x: x['family'] == 'windows-license' and 'veeam' not in x['invoiceName'].lower(), dict.values(plan_codes))
    
    computed_plans = []
    for p in plans:
        for cores in list_of_cores:
            invoiceName = ' '.join(map(lambda x: x.capitalize(), p['invoiceName'].split('-')))
            item = {'type': 'Licence', 'description': invoiceName.capitalize() + f' - {cores} Cores' }
            for con in CONFORMITY + ['snc']:
                item['price_'+con] = p['price_default'] * cores
            # del item['family']
            computed_plans.append(item)

    return computed_plans

def get_veeam_and_zerto_licenses(sub='FR'):
    if sub == 'DE':
        sub = 'en-ie'
    elif sub == 'US':
        sub = 'en'
    tries = [sub, f'en-{sub}', f'fr-{sub}']
    RE_PRICE = r'<span class="price-value">[\D]+([\d]+[,\.]?[\d]+).*<\/span>'
    veeam_price = 0
    zerto_price = 0
    for s in tries:
        try:
            veam_html = get_html(f'https://www.ovhcloud.com/{s.lower()}/storage-solutions/veeam-enterprise/')
            res = re.findall(RE_PRICE, veam_html)
            if bool(res):
                veeam_price = float(res[0].replace(',', '.'))

            zerto_html = get_html(f'https://www.ovhcloud.com/{s.lower()}/hosted-private-cloud/vmware/zerto/')
            res = re.findall(RE_PRICE, zerto_html)
            if bool(res):
                zerto_price = float(res[0].replace(',', '.'))
            break
        except urllib.error.HTTPError: # 404 not found
            veeam_price = 0
    veam = {'type': 'Licence', 'description': 'Veeam Entreprise plus License - per VM'}
    zerto = {'type': 'Licence', 'description': 'Zerto License - per VM'}
    for con in CONFORMITY:
        veam['price_'+con] = veeam_price
        zerto['price_'+con] = zerto_price
    veam['price_snc'] = round(veeam_price*SNC_MARKUP)
    zerto['price_snc'] = round(zerto_price*SNC_MARKUP)

    return list(filter(lambda x: x['price_default'] > 0, [veam, zerto]))

def get_pcc_ranges_and_windows_licenses(sub='FR'):
    pcc_plans = get_json(f'{get_base_api(sub)}/1.0/order/catalog/formatted/privateCloud?ovhSubsidiary={sub}')
    print(f'{get_base_api(sub)}/1.0/order/catalog/formatted/privateCloud?ovhSubsidiary={sub}')

    plan_codes = {}
    for plans in pcc_plans['plans']:
        plan_codes |= get_addon_families(plans)

    cores_quandidates = set([10,6,8,20])
    catalog = []
    for cr in pcc_plans['commercialRanges']:
        if cr['name'] not in RANGES or not cr['datacenters'][0]['hypervisors'][0]['orderable']:
            continue
        
        # zones = list(map(lambda dc: dc['cityCode'], cr['datacenters']))
        # if cr['name'] in SNC_RANGES:
        #     zones += TZ_REGION
        managementFeePlanCode = cr['datacenters'][0]['managementFees']['planCode']
        nsxt_vdc_option = cr['datacenters'][0]['nsxt-vdc-option'] if 'nsxt-vdc-option' in cr['datacenters'][0] else None
        nsxt_ip_option = cr['datacenters'][0]['nsxt-ip-block'] if 'nsxt-ip-block' in cr['datacenters'][0] else None

        # List hosts spec
        for h in cr['datacenters'][0]['hypervisors'][0]['hosts']:
            if 'hourly' in h['name'].lower() or h['planCode'] not in plan_codes:
                continue

            cpuspec = h['specifications']['cpu']
            cpu_text = f"{cpuspec['model']} - {cpuspec['frequency']['value']} {cpuspec['frequency']['unit']} - {cpuspec['cores']} cores/{cpuspec['threads']} Threads"
            ram_text = f"{h['specifications']['memory']['ram']['value']} {h['specifications']['memory']['ram']['unit']}"

            # Pack & Host
            nsxt_vdc_option_price = plan_codes[nsxt_vdc_option['planCode']] if nsxt_vdc_option is not None else None
            nsxt_ip_option_price = plan_codes[nsxt_ip_option['planCode']] if nsxt_ip_option is not None else None
            pack_datastore = plan_codes[h['storagesPack'][0]] # always X2 this value
            pack = {'range': cr['name'], 'type': 'Pack', 'description': f"2x Host {h['name']} \n  - {cpu_text}\n  - {ram_text} \n{STORAGE_PACK_DESCRIPTION}"}
            host = {'range': cr['name'], 'type': 'Host', 'description': f"Additional Host {h['name']}\n{cpu_text}\n{ram_text}"} | plan_codes[h['planCode']]
            cores_quandidates.add(h['specifications']['cpu']['cores'])

            for conformity in CONFORMITY:
                if cr['name'] == 'essentials' and conformity != 'default':
                    continue
                price_key = f"price_{conformity}"
                price_host = plan_codes[h['planCode']][price_key]
                
                # CRITICAL PRICING FORMULA FOR PACKS
                pack_price = nsxt_vdc_option_price[price_key] if nsxt_vdc_option_price is not None else 0
                pack_price += nsxt_ip_option_price[price_key] if nsxt_ip_option_price is not None else 0
                pack_price += pack_datastore[price_key] * 2 + plan_codes[managementFeePlanCode][price_key] + 2 * price_host 
                pack[price_key] = pack_price

                if cr['name'] != 'essentials' and conformity == 'default':
                    pack['price_snc'] = round(pack_price * SNC_MARKUP)
                    host['price_snc'] = round(price_host * SNC_MARKUP)

            # NSX_T packs contains /28 IP Block
            if cr['name'] == 'nsx-t':
                pack['description'] += '\n  - IP Block /28 (16 IPs)'

            catalog.append(pack)
            catalog.append(host)

        # List options
        for opt in cr['datacenters'][0]['hypervisors'][0]['options'] + cr['datacenters'][0]['hypervisors'][0]['servicePacks'] + cr['datacenters'][0]['hypervisors'][0]['storages']:
            if opt['planCode'] not in plan_codes:
                continue
            option = deepcopy(plan_codes[opt['planCode']])
            if 'ip' in option['invoiceName'].lower():
                option['description'] = option['invoiceName'].replace('RIPE', '') if 'RIPE' in option['invoiceName'] else option['invoiceName'].replace('ARIN', '')
                ip_count = 2**(32 - int(option['description'].split('/')[-1]))
                option['description'] += f" {ip_count} Public IPs"
                option['type'] = 'Public IP'
                option['price_snc'] = option['price_default']
                catalog.append(option)
            elif 'datastore' in option['invoiceName'].lower():
                option['description'] = f"Additional Datastore - {opt['specifications']['type']} {opt['specifications']['size']['value']} {opt['specifications']['size']['unit']}"
                option['type'] = 'Datastore'
                option['price_snc'] = round(option['price_default'] * SNC_MARKUP)
                catalog.append(option)

        catalog += get_backup_options(plan_codes) + parse_windows_licenses(plan_codes, cores_quandidates)

    return catalog

def privatecloud():
    subs = {}
    for sub in ['FR']: # SUBSIDIARIES:
        products = {
            'date': datetime.now().isoformat(),
            'locale': get_json(f'{get_base_api(sub)}/1.0/order/catalog/public/cloud?ovhSubsidiary={sub}')['locale'],
        }

        catalog = get_pcc_ranges_and_windows_licenses(sub)
        if products['locale']['currencyCode'] == 'EUR':
            catalog += SNC_PRODUCTS
        catalog += get_occ_options(sub)
        catalog += get_ip_lb(sub)
        catalog += get_veeam_and_zerto_licenses(sub)
        catalog += get_ps(sub)

        # Sanatize columns
        df = pd.DataFrame(catalog)
        df.drop_duplicates(['description', 'price_default'], inplace=True)
        df.drop(['family', 'invoiceName'], inplace=True, axis=1)
        df['range'] = df['range'].fillna('').apply(lambda x: x.upper())
        df.fillna(0, inplace=True)

        products['catalog'] = df.to_dict('records')
        subs[sub] = products

    # json.dump(subs, open('tmp.json', 'w+'))
    upload_gzip_json(subs, f'private-cloud.json', S3_BUCKET)

if __name__ == '__main__':
    privatecloud()