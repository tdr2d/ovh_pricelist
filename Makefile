ENDPOINT := https://s3.gra.io.cloud.ovh.net/  # PROD
ENDPOINT_DEV := https://s3.sbg.io.cloud.ovh.net/

help: ## Show this help
	@grep -E "^[a-z_-]+:|^##" Makefile | sed -E 's/([\s_]+):.*##(.*)/\1:\2/' | column -s: -t | sed -e 's/##//'

build: ## build static html files
	jinja templates/index.html -E S3_BUCKET -E S3_REGION -o static/index.html
	jinja templates/private-cloud.html -E S3_BUCKET -E S3_REGION -o static/private-cloud.html
	jinja templates/public-cloud.html -E S3_BUCKET -E S3_REGION -o static/public-cloud.html

upload_static:
	export S3_BUCKET=share
	S3_BUCKET=share S3_REGION=gra $(MAKE) build
	aws s3 --endpoint-url $(ENDPOINT) sync --acl public-read static s3://share/

purge_s3_objects:
	s3-client -e $(ENDPOINT) -r gra listobj share | grep static | cut -d' ' -f 2 |  xargs -I{} s3-client -e $(ENDPOINT) -r gra deleteobj share {}

upload_jobs:
	ls jobs/*.py |  xargs -I{} aws s3 --endpoint-url $(ENDPOINT) cp --acl public-read {} s3://share/{}
