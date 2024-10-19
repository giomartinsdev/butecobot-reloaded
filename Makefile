docker-build-base:
	docker buildx build -t brunofunnie/butecobot-reloaded-php:amd64-latest --platform=linux/amd64 -f docker/base.dockerfile docker
	docker buildx build -t brunofunnie/butecobot-reloaded-php:arm64v8-latest --platform=linux/arm/v8 -f docker/base.dockerfile docker
build-app:
	docker buildx build -t brunofunnie/butecobot-reloaded-app:latest --platform=linux/amd64 -f docker/app.dockerfile .
dev:
	docker buildx build -t brunofunnie/butecobot-reloaded-app:latest --platform=linux/arm/v8 -f docker/app.dockerfile .
	docker compose down butecobot-reloaded; docker compose up butecobot-reloaded
dev-essentials:
	docker compose up -d mysql pma valkey mpit mongo mongo-express
push:
	docker push brunofunnie/butecobot-reloaded-php:arm64v8-latest
	docker push brunofunnie/butecobot-reloaded-php:amd64-latest
	docker manifest create brunofunnie/butecobot-reloaded-php:latest \
	--amend brunofunnie/butecobot-reloaded-php:amd64-latest \
	--amend brunofunnie/butecobot-reloaded-php:arm64v8-latest
	docker manifest push brunofunnie/butecobot-reloaded-php:latest
