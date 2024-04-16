import ssl
import os
import boto3
import gzip
import json
import urllib.request
import time
from itertools import product
import traceback

ssl._create_default_https_context = ssl._create_unverified_context

S3_ACCESS_KEY_ID = os.getenv('S3_ACCESS_KEY_ID')
S3_SECRET_ACCESS_KEY = os.getenv('S3_SECRET_ACCESS_KEY')
S3_BUCKET = os.getenv('S3_BUCKET')
S3_REGION = os.getenv('S3_REGION', 'sbg') 

SUBSIDIARIES = ['CA', 'DE','ES','FR','GB','IE','IT','MA','NL','PL','PT','SN','TN'] # ,'US']
print(f'Bucket is {S3_BUCKET}, region is {S3_REGION}')
if 'dev' in S3_BUCKET:
    SUBSIDIARIES = ['FR']
TZ_DCS = ['RBX', 'SBG']

API_US = 'https://api.us.ovhcloud.com'
API_EU = 'https://api.ovh.com'
API_CA = 'https://ca.api.ovh.com'
SNC_MARKUP = 1.12
ENCODING_PREFIXES = {
    'bm': 'b-',  # Prefix baremetal catalog
    'pcc': 'q-', # Prefix private cloud catalog
    'pci': 'p-', # Prefix public cloud catalog
}

def index_catalog(catalog, prefix):
    index = {}
    keys = product('abcdefghijklmnoprstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', repeat=2) # 3844 uniq keys
    for item in catalog:
        key = prefix + ''.join(next(keys))
        index[key] = item
    return index

def get_base_api(sub):
    base_api = API_EU
    if sub == 'US':
        base_api = API_US
    elif sub == 'CA':
        base_api = API_CA
    return base_api


def get_website_tries_for_country(sub):
    if sub == 'DE':
        sub = 'en-ie'
    elif sub == 'US':
        sub = 'en'
    return [sub, f'en-{sub}', f'fr-{sub}']

def s3():
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#examples
    return boto3.client(
        "s3",
        endpoint_url=f"https://s3.{S3_REGION}.io.cloud.ovh.net/",
        region_name=S3_REGION,
        aws_access_key_id=S3_ACCESS_KEY_ID,
        aws_secret_access_key=S3_SECRET_ACCESS_KEY,
    )

def upload_json(jsonObject, filename, bucket=S3_BUCKET):
    return s3().put_object(Body=json.dumps(jsonObject), Bucket=bucket, Key=filename, ContentType='application/json', ACL='public-read')

def upload_gzip_json(jsonObject, filename, bucket=S3_BUCKET):
    body = gzip.compress(bytes(json.dumps(jsonObject), encoding='utf-8'))
    return s3().put_object(Body=body, Bucket=bucket, Key=filename, ContentType='application/json', ContentEncoding='gzip', ACL='public-read')

def get_html(url):
    req = urllib.request.Request(url) 
    return urllib.request.urlopen(req).read().decode("utf-8")

def get_json(url):
    req = urllib.request.Request(url, headers={'Accept': 'application/json'}) 
    return json.loads(urllib.request.urlopen(req).read().decode("utf-8"))


def exponential_backoff(fun, tries=5):
    for i in range(tries):
        try:
            return fun()
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            print(f'Retrying {i}')
            time.sleep(2**i)
    raise ValueError("Number of tries exceeded")