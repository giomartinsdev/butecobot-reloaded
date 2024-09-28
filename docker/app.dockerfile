FROM brunofunnie/butecobot-reloaded-php:latest

WORKDIR /app

COPY builds/laracord .

ENTRYPOINT ["/entrypoint.sh"]
