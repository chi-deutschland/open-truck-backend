# Run Makefile like this:
# make VERSION=v0.0.1 SERVICE=test-service STAGE=development google

google: update_version build push deploy

# Basic config
$(eval PROJECT_ID = $(shell gcloud config get-value project))
SERVICE ?=
VERSION ?=
STAGE ?=

update_version:
	echo VERSION > ./VERSION

build:
	docker buildx build \
		--platform linux/amd64 \
		--build-arg STAGE=$(STAGE) . \
		--tag gcr.io/$(PROJECT_ID)/$(SERVICE):$(VERSION)

push:
	docker push gcr.io/$(PROJECT_ID)/$(SERVICE):$(VERSION)

deploy:
	gcloud run deploy $(SERVICE) \
		--image gcr.io/$(PROJECT_ID)/$(SERVICE):$(VERSION) \
		--memory="256Mi" \
        --platform managed \
		--allow-unauthenticated \
        --max-instances=1 \
		--set-env-vars "STAGE=$(STAGE)" \
		--set-env-vars "VERSION=$(VERSION)"