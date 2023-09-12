#!/bin/bash

VERSION=2.3.0

# S3 configuration
cat << EOF > cors.json
{
    "CORSRules": [
         {
             "AllowedHeaders": ["Authorization"],
             "AllowedMethods": ["GET", "HEAD"],
             "AllowedOrigins": ["*"],
             "ExposeHeaders": ["Access-Control-Allow-Origin"]
         }
    ]
}
EOF
aws s3api put-bucket-cors --bucket share --cors-configuration file://cors.json --endpoint-url=https://s3.gra.io.cloud.ovh.net/

# K8s Configuration
cd manifests 
kubectl create ns ovh-pricelist

kubectl apply -f deployment-pricelist.yml
kubectl expose deployment ovh-pricelist --port 80 --target-port 80 -n ovh-pricelist
kubectl create ingress ovh-pricelist-tls -n ovh-pricelist --class=default --rule="pricelist.ovh/*=ovh-pricelist:80,tls=ovh-pricelist-cert" --class nginx \
    --annotation cert-manager.io/cluster-issuer=letsencrypt

kubectl apply -f deployment-calculator.yml
kubectl expose deployment ovh-calculator --port 80 --target-port 80 -n ovh-pricelist
kubectl create ingress ovh-calculator-tls -n ovh-pricelist --class=default --rule="ovh-calculator.ovh/*=ovh-calculator:80,tls=ovh-calculator-cert" --class nginx \
    --annotation cert-manager.io/cluster-issuer=letsencrypt

# K8S Cronjob for computing plans
docker build -t tdr2d/ovh_pricelist:${VERSION}-job .
docker push tdr2d/ovh_pricelist:${VERSION}job

# deploy it
kubectl apply -f jobs/cronjob.yml