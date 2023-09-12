export MATCH=*
ENDPOINT := https://s3.gra.io.cloud.ovh.net/  # PROD
ENDPOINT := https://s3.sbg.io.cloud.ovh.net/  # DEV
BUCKET := s3://${S3_BUCKET}

help: ## Show this help
	@grep -E "^[a-z0-9_-]+:|^##" Makefile | sed -E 's/([\s_]+):.*##(.*)/\1:\2/' | column -s: -t | sed -e 's/##//'

serve: ## dev http server
	cd static && python3 -m http.server 80

build: ## build static html files
	jinja templates/calculator.html -E S3_BUCKET -E S3_REGION -o static/calculator.html
	# jinja templates/index.html -E S3_BUCKET -E S3_REGION -o static/index.html
	# jinja templates/private-cloud.html -E S3_BUCKET -E S3_REGION -o static/private-cloud.html
	jinja templates/public-cloud.html -E S3_BUCKET -E S3_REGION -o static/public-cloud.html

upload_static:
	# @export S3_BUCKET=share
	# @S3_BUCKET=share S3_REGION=gra $(MAKE) build
	aws s3 --endpoint-url $(ENDPOINT) sync --delete --acl public-read static $(BUCKET)/static
	find ./static/lib/ -type f -exec gzip -9 "{}" \; -exec mv "{}.gz" "{}" \;
	ls ./static/lib | xargs -I{} aws s3api --endpoint-url $(ENDPOINT) put-object --key static/lib/{} --body static/lib/{} --bucket ${S3_BUCKET} --content-type gzip --acl public-read
	gunzip -f -S '' ./static/lib/*

purge_s3_objects: ## Usage MATCH='lib/*' make purge_s3_objects
	aws s3 --endpoint-url $(ENDPOINT) rm $(BUCKET) --recursive --exclude="*" --include="${MATCH}"

upload_jobs:
	ls jobs/*.py |  xargs -I{} aws s3 --endpoint-url $(ENDPOINT) cp --acl public-read {} $(BUCKET){}
