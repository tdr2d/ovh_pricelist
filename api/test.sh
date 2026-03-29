#!/bin/bash

curl -X POST -H "Content-Type: application/json" \
    -d'{"data": "", "total_mrr": 100.13, "author": "author1", "title": "quote1", "subsidiary": "fr"}'\
     localhost:8080/api-endpoint

# curl -X POST -H "Content-Type: application/json" \
#     -d'{"data": "", "total_mrr": "", "author": "author1", "title": "quote1", "subsidiary": "fr"}'\
#      localhost:8080/api-endpoint