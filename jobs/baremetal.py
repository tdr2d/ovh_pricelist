from datetime import datetime
from utils import *
import pandas as pd

def index_addons(js):
    addon_per_plancode = {}
    for addon in js['addons']:
        for price in addon['pricings']:
            if price['commitment'] == 0 and price['mode'] == 'default' and price['interval'] == 1:
                addon_per_plancode[addon['planCode']] = {'planCode': addon['planCode'], 'invoiceName': addon['invoiceName'], 'product': addon['product'] , 'price': price['price'] / 100000000}
    return addon_per_plancode

def index_products(js):
    products = {}
    for product in js['products']:
        if product['blobs']:
            products[product['name']] = product['blobs']['technical']
    return products

def build_dataset(js):
    plans = []
    server_options = [] # price, description, server name
    addons = index_addons(js)
    products = index_products(js)

    # Loop on servers
    for plan in js['plans']:
        server_name = plan['invoiceName'].upper().replace('ADVANCE', 'ADV').split(' ')[0]
        base_addon_options = { 'priv_bp': None, 'pub_bp': None, 'memory': None, 'storage': None, 'storage_system': None}
        tech_specs = products[plan['planCode']] if plan['planCode'] in products else products[plan['product']]
        server_range = 'high-grade' if tech_specs['server']['range'] == 'hgr' else tech_specs['server']['range']
        server_price = next(filter(lambda x: x['commitment'] == 0 and x['mode'] == 'default' and x['interval'] == 1, plan['pricings']))['price'] / 100000000

        # Loop on server options (ram,storage,bandwidth)
        if not len(plan['addonFamilies']):
            continue
        for addon_family in plan['addonFamilies']:
            if addon_family['name'] == 'memory':
                for x in addon_family['addons']:
                    item = {'range': server_range, 'price': addons[x]['price'], 'name': server_name, 'setupfee': 0 }
                    item['description'] = f"{item['name']} - RAM Option: {addons[x]['invoiceName']}"
                    if item['price'] == 0:
                        base_addon_options['memory'] = addons[x]
                    else:
                        server_options.append(item)

            elif addon_family['name'] == 'storage' or addon_family['name'] == 'disk':
                for x in addon_family['addons']:
                    item = {'range': server_range, 'price': addons[x]['price'], 'name': server_name, 'setupfee': 0 }
                    item['description'] = f"{item['name']} - Storage Option: {addons[x]['invoiceName']}"
                    if item['price'] == 0:
                        base_addon_options['storage'] = addons[x]
                    else:
                        server_options.append(item)
            elif addon_family['name'] == 'system-storage':
                base_addon_options['storage_system'] = addons[addon_family['addons'][0]]
            elif addon_family['name'] in ['vrack', 'bandwidth']:
                for x in addon_family['addons']:
                    item = {'range': server_range, 'price': addons[x]['price'], 'name': server_name, 'setupfee': 0 }
                    item['description'] = f"{item['name']} - {'Private' if addon_family['name'] == 'vrack' else 'Public'} Bandwidth Option: {addons[x]['invoiceName']}"

                    if item['price'] == 0 and addon_family['name'] == 'vrack':
                        base_addon_options['priv_bp'] = addons[x]
                    elif item['price'] == 0 and addon_family['name'] == 'bandwidth':
                        base_addon_options['pub_bp'] = addons[x]
                    else:
                        server_options.append(item)
        
        # print(server_name)
        # print(server_price)
        # print(base_addon_options)
        # print(plan)

        storage_specs = products[base_addon_options['storage']['product']]
        memory_specs = products[base_addon_options['memory']['product']]

        # price = server_price + base_addon_options['storage']['price'] + base_addon_options['memory']['price']
        # print(base_addon_options['memory']['price'])
        storage_amount = storage_specs['storage']['disks'][0]['number'] * storage_specs['storage']['disks'][0]['capacity']
        if (len(storage_specs['storage']['disks']) > 1 and storage_specs['storage']['disks'][1]['number'] != ''):
            storage_amount += storage_specs['storage']['disks'][1]['number'] * storage_specs['storage']['disks'][1]['capacity']
        storage_amount = round(storage_amount / 1000)
        
        item = {
            'range': 'high-grade' if tech_specs['server']['range'] == 'hgr' else tech_specs['server']['range'],
            'name': server_name,
            'cpu_model': f"{tech_specs['server']['cpu']['brand']} {tech_specs['server']['cpu']['model']}",
            'cpu_cores': tech_specs['server']['cpu']['cores'],
            'cpu_threads': tech_specs['server']['cpu']['threads'],
            'cpu_speed': tech_specs['server']['cpu']['frequency'],
            'ram': base_addon_options['memory']['invoiceName'], 
            'ram_size': memory_specs['memory']['size'],
            'ram_speed': memory_specs['memory']['frequency'],
            'ram_type': memory_specs['memory']['ramType'],
            'storage': base_addon_options['storage']['invoiceName'],
            'storage_type': ' + '.join(list(map(lambda x: x['technology'], storage_specs['storage']['disks']))),
            'storage_raid_type': storage_specs['storage']['raid'],
            'storage_total_tbytes': storage_amount,
            'setupfee': server_price,
            'price': server_price, 'price_snc': 0,
        }

        item['description'] = f"Dedicated Server {item['name']}\n"
        item['description'] += f"CPU: {tech_specs['server']['cpu']['brand']} {tech_specs['server']['cpu']['model']} {tech_specs['server']['cpu']['cores']} Cores/{tech_specs['server']['cpu']['threads']} Threads\n"
        item['description'] += f"RAM: {base_addon_options['memory']['invoiceName']}\n"
        item['description'] += f"Storage: {base_addon_options['storage_system']['invoiceName'] + ' + ' if base_addon_options['storage_system'] else ''}{base_addon_options['storage']['invoiceName']}\n"
        item['description'] += f"Default Public Bandwidth: {base_addon_options['pub_bp']['invoiceName']}"
        if base_addon_options['priv_bp'] is not None:
            item['description'] += f"\nDefault Private Bandwidth: {base_addon_options['priv_bp']['invoiceName']}"

        if tech_specs['server']['range'].lower() in ['scale', 'hgr']:
            item['price_snc'] = round(server_price * SNC_MARKUP)
        if item['price'] > 0:
            plans.append(item)

    return plans + server_options

def postprocessing(dataset):
    df = pd.DataFrame(dataset)
    df = df.drop_duplicates(subset=['description'])
    df = df.fillna('')
    return df.to_dict('records')

# TODO GROUP all sub in one file
def baremetal():
    for sub in ['FR']:
        base_api = get_base_api(sub)
        data = get_json(f'{base_api}/v1/order/catalog/public/baremetalServers?ovhSubsidiary={sub}')
        
        dataset = build_dataset(data)
        dataset = postprocessing(dataset)
        print(len(dataset))
        json.dump(dataset, open('tmp.json', 'w+'))
        assert len(dataset) > 500, "Must have more than 1k refs"
        filename = f'baremetal_prices/{sub.lower()}.json'
        index = add_index(dataset)
        data = { 'plans': dataset, 'date': datetime.now().isoformat(), 'currency': data['locale']['currencyCode'] }
        upload_gzip_json(data , filename, S3_BUCKET)
        print(f'INFO: Uploaded {filename}')
        yield data, index

if __name__ == '__main__':
    # print('HERE')
    list(baremetal())