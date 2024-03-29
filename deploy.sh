#!/bin/bash

VERSION=2.3.0

# nginx ingress
helm upgrade --install -n default -f manifests/nginx-ingress-values.yml ingress-nginx ingress-nginx/ingress-nginx

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
kubectl create ns pricelist

# Secret for basic auth
htpasswd -c auth XXusernameXX
kubectl create secret generic pricelist-basic-auth --from-file=auth

kubectl apply -f deployment-pricelist.yml
kubectl expose deployment pricelist --port 80 --target-port 80 -n pricelist
kubectl create ingress pricelist-tls -n pricelist --class=default --rule="pricelist.ovh/*=pricelist:80,tls=pricelist-cert" --class nginx \
    --annotation cert-manager.io/cluster-issuer=letsencrypt \
    --annotation nginx.ingress.kubernetes.io/auth-realm='Authentication Required' \
    --annotation nginx.ingress.kubernetes.io/auth-type=basic \
    --annotation nginx.ingress.kubernetes.io/auth-secret=pricelist-basic-auth


# K8S Cronjob for computing plans
docker build -t tdr2d/ovh_pricelist:${VERSION}-job .
docker push tdr2d/ovh_pricelist:${VERSION}job

# deploy it
kubectl apply -f jobs/cronjob.yml