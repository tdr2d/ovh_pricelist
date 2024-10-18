# OVHcloud pricelist and calculator
Webpage showing OVHcloud catalogue and calculator.
Aim is to browse quickly the vast OVHcloud catalog with all the derivatives.

Prices are taken from api.ovh.com for different countries including Europe, Canada.
Official prices can be found at :
- Private Cloud https://www.ovhcloud.com/en/hosted-private-cloud/vmware/prices/
- Public Cloud https://www.ovhcloud.com/fr/public-cloud/prices/
- Baremetal Cloud https://www.ovhcloud.com/fr/bare-metal/prices/

It does not support the USA.

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
- improve select input, prevent closing when unfocus
- ability to add custom input
- move up and down line
- BUG frontend with item having 0 values, it defaults to 1.
- BUG only apply floating precision to unit/price instead of total price