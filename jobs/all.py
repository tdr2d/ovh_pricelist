from baremetal import baremetal
from privatecloud import privatecloud
from publiccloud import publiccloud
from utils import *
import datetime
import json
import gzip

# sufixes = {
#     'custom': 'i-',
#     'baremetal': 'b-',
#     'privatecloud': 'P-',
#     'publiccloud': 'p-',
#     'condition': 'c-',
#     'zone': 'z-',
#     'index_version': 'v[0-9]+,
# }
# conditions = 'abcdefghij'

# format v-1z-Roubaix Zone de Confiance'- adb-aa-0.123z36z15b-zac-abcdefghij-1249-isdsdgsd-1241

def save_indexes(bm, pcc=None, pci=None):
    for sub in ['FR']:
        version = 0
        try:
            last_index = s3().get_object(Bucket=S3_BUCKET, Key=f'pricelistindex/index_{sub.lower()}.json')
            last_index_content = json.loads(gzip.decompress(last_index['Body'].read()))
            print(f"Found index version: {last_index_content['version']}")
            version = last_index_content['version'] + 1
        except boto3.resource('s3').meta.client.exceptions.NoSuchKey:
            pass
    
        _, bm_index = next(bm)
        subsidiary_index = {
            'version': version,
            'date': datetime.datetime.now().isoformat(),
            'index_baremetal': bm_index,
            # 'index_publiccloud': pci[sub][1],
            # 'index_privatecloud': pcc[sub][1],
        }
        upload_gzip_json(subsidiary_index, f'pricelistindex/index_{sub.lower()}.json')
        upload_gzip_json(subsidiary_index, f'pricelistindex/index_{sub.lower()}_v{version}.json')


if __name__ == '__main__':
    print('Getting Baremetal Catalog')
    bm_catalog_gen = exponential_backoff(baremetal)
    save_indexes(bm_catalog_gen)

    # print('Getting Private Cloud Catalog')
    # privatecloud_cat_idx = exponential_backoff(privatecloud)
    # print('Getting Public Cloud Catalog')
    # publiccloud_cat_idx = exponential_backoff(publiccloud)
