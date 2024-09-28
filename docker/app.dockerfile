FROM brunofunnie/butecobot-reloaded-php:arm64v8-latest

WORKDIR /app

COPY builds/laracord .

ENTRYPOINT ["/entrypoint.sh"]
