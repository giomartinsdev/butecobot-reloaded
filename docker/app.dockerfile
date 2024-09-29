FROM brunofunnie/butecobot-reloaded-php:latest

WORKDIR /app

COPY . /src/

RUN cd /src && composer install --no-dev --optimize-autoloader --no-interaction

COPY docker/confs/entrypoint.sh /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
