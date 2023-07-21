# OVHcloud pricelist
Build a webpage showing OVHcloud baremetal servers pricelist.
Aim is to browse quickly the vast OVHcloud servers catalog. I list all the derivatives.
A server with 2 memory options and 4 storages option will appear in 2x4 = 8 lines.


## Live demo
You can test it via https://pricelist.ovh

## Features
Thanks to datatables.net scripts :
* Table view of all OVH.com dedicated servers with hardware, price, and few other informations.
* Sorting and filtering
* Export to CSV / EXCEL / PDF / JSON


## OVHcloud API structure for servers
### API for server specifications and prices

For OVHcloud european information system, the API endpoints for retrieving servers specifications and prices are :


- Classic ranges: https://api.ovh.com/console/#/order/catalog/public/baremetalServers#GET

The JSON structure need some clarifications :

```
{
    order.catalog.public.DedicatedServerCatalog: {
        description: "Describes a Dedicated server Catalog inside a Subsidiary",
        properties: {
            addons: { … },
            catalogId: { … },
            locale: { … },
            planFamilies: { … },
            plans: { … },
            products: { … }
        }
    }

}
```

* `addons` : memory, storage, network, ... components are detailed as addons. Each addon has a planCode, a product and pricings. Technical specifications are not here.
* `catalogId` : A version number. when the OVHcloud catalog is updated, the version number is incremented.
* `locale` : Details the currencyCode used, the subsidiay, and the tax rate (prices may vary based on the country selected)
* `planFamilies` : not used
* `plans` : A plan is a combination or a product, addons, attached to pricings.
* `products` : A product

To sum up, plans and addons are composed of products and pricings, and servers plans will contain addons.
Only products contains technical specifications.

Here is an example showing nesting between JSON elements :


```
+-------------------------------------------------------------------------------------------------+
|Example : get ADVANCE-1 RAM specifications via OVH.com API /order/catalog/public/baremetalServers|
+-------------------------------------------------------------------------------------------------+

+---plans : invoiceName = ADVANCE-1------+
|                                        |     +---> +---Addons : planCode = ram-32-adv1-----+
|planCode : 19adv01                      |     |     |                                       |
|                                        |     |     |invoiceName : 32GB DDR4 ECC 2400MHz    |
|addons families                         |     |     |                                       |
|  +---memory-------------------------+  |     |     |pricings                               |
|  |ram-32g-adv1                      +--------+     |  +---------------------------------+  |
|  |ram-64g-adv1                      |  |           |  |1 month                          |  |
|  +----------------------------------+  |           |  +---------------------------------+  |
|  +---storage------------------------+  |           |  +---------------------------------+  |
|  |softraid-2x1000nvme-adv           |  |           |  |... (more pricings)              |  |
|  |softraid-3x1000nvme-adv           |  |           |  +---------------------------------+  |
|  |... (more addons)                 |  |           |                                       |
|  |hardraid-4x960ssd-adv             |  |      +----+product : ram-32g-ecc-2400             |
|  +----------------------------------+  |      |    |                                       |
|  +---vrack--------------------------+  |      |    +---------------------------------------+
|  |vrack-bandwidth-100-included      |  |      |
|  |vrack-bandwidth-1000-option       |  |      |
|  +----------------------------------+  |      |
|                                        |      |
|pricings                                |      +--> +---products : name = ram-32g-ecc-2400--+
|  +----------------------------------+  |           |                                       |
|  |setup fees                        |  |           | memory                                |
|  +----------------------------------+  |           |  +---------------------------------+  |
|  +----------------------------------+  |           |  |frequency : 2400                 |  |
|  |1 month                           |  |           |  |ecc : true                       |  |
|  +----------------------------------+  |           |  |ramType : DDR4                   |  |
|  +----------------------------------+  |           |  |size : 32                        |  |
|  |12 months                         |  |           |  +---------------------------------+  |
|  +----------------------------------+  |           |                                       |
|  +----------------------------------+  |           +---------------------------------------+
|  |24 months                         |  |
|  +----------------------------------+  |
|                                        |
|product : 19adv01                       |
|                                        |
+----------------------------------------+
```
