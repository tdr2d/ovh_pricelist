# OVHcloud pricelist and calculator
Webpage showing OVHcloud catalogue and calculator.
Aim is to browse quickly the vast OVHcloud catalog with all the derivatives.

Prices are taken from api.ovh.com for different countries including Europe, Canada and the USA.
Official prices can be found at :
- Private Cloud https://www.ovhcloud.com/en/hosted-private-cloud/vmware/prices/
- Public Cloud https://www.ovhcloud.com/fr/public-cloud/prices/
- Baremetal Cloud https://www.ovhcloud.com/fr/bare-metal/prices/


## Live
* Pricelist https://pricelist.ovh
* Calculator https://pricelist.ovh/calculator.html

## Features
* Table view of all ovhcloud.com catalogue with hardware, price, and few other informations.
* Sorting and filtering
* Export to CSV / EXCEL / PDF / JSON
* Price estimate
* Quote generator


### TODO
Baremetal bug:
  File "/Users/tducrot/tdr2d/ovh_pricelist/jobs/baremetal.py", line 30, in build_dataset
    tech_specs = products[plan['planCode']] if plan['planCode'] in products else products[plan['product']]
KeyError: '23cluster-24hci-a1-01'

Remove ZONE rows, create a zone column instead, reduce size of text to 0,7rem
BUG PHrase de commit condition > 1 not true
BUG only apply floating precision to unit/price instead of total price