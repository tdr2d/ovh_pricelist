export MATCH=*
ENDPOINT := https://s3.gra.io.cloud.ovh.net/  # PROD
# ENDPOINT := https://s3.sbg.io.cloud.ovh.net/  # DEV
BUCKET := s3://${S3_BUCKET}

help: ## Show this help
	@grep -E "^[a-z0-9_-]+:|^##" Makefile | sed -E 's/([\s_]+):.*##(.*)/\1:\2/' | column -s: -t | sed -e 's/##//'

build: ## build static html files, for prod use : S3_REGION=gra S3_BUCKET=share make build
	jinja templates/calculator.html -E S3_BUCKET -E S3_REGION -o static/calculator.html
	jinja templates/baremetal.html -E S3_BUCKET -E S3_REGION -o static/baremetal.html
	jinja templates/private-cloud.html -E S3_BUCKET -E S3_REGION -o static/private-cloud.html
	jinja templates/public-cloud.html -E S3_BUCKET -E S3_REGION -o static/public-cloud.html
	jinja templates/public-cloud-enterprise.html -E S3_BUCKET -E S3_REGION -o static/public-cloud-enterprise.html

serve: build ## dev http server
	cd static && python3 -m http.server 80

upload_static_prod: ## Usage for prod: S3_BUCKET=share S3_REGION=gra make upload_static_prod
	S3_BUCKET=share S3_REGION=gra $(MAKE) build
	aws s3 --endpoint-url $(ENDPOINT) sync --delete --acl public-read static s3://share/static
	find ./static/lib/ -type f -exec gzip -9 "{}" \; -exec mv "{}.gz" "{}" \;
	ls static/lib/*.js | xargs -I{} aws s3api --endpoint-url $(ENDPOINT) put-object --key {} --body {} --bucket share --content-type text/javascript --content-encoding gzip --acl public-read
	ls static/lib/*.css | xargs -I{} aws s3api --endpoint-url $(ENDPOINT) put-object --key {} --body {} --bucket share --content-type text/css --content-encoding gzip --acl public-read
	gunzip -f -S '' ./static/lib/*

.PHONY: jobs
jobs:
	cd jobs && python3 all.py

jobs_prod:
	S3_BUCKET=share S3_REGION=gra $(MAKE) jobs

purge_s3_objects: ## Usage MATCH='lib/*' make purge_s3_objects
	aws s3 --endpoint-url $(ENDPOINT) rm $(BUCKET) --recursive --exclude="*" --include="${MATCH}"

upload_jobs:
	ls jobs/*.py |  xargs -I{} aws s3 --endpoint-url $(ENDPOINT) cp --acl public-read {} $(BUCKET){}
