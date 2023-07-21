ENDPOINT := https://s3.gra.io.cloud.ovh.net/

help: ## Show this help
	@grep -E "^[a-z_-]+:|^##" Makefile | sed -E 's/([\s_]+):.*##(.*)/\1:\2/' | column -s: -t | sed -e 's/##//'

build:
	jinja templates/index.html -o static/index.html
	jinja templates/private-cloud.html -o static/private-cloud.html
	jinja templates/public-cloud.html -o static/public-cloud.html

upload_static:
	aws s3 --endpoint-url $(ENDPOINT) sync --acl public-read static s3://share/

delete_static:
	s3-client -e $(ENDPOINT) -r gra listobj share | grep static | cut -d' ' -f 2 |  xargs -I{} s3-client -e $(ENDPOINT) -r gra deleteobj share {}
