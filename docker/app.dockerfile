FROM brunofunnie/butecobot-reloaded-php:latest

WORKDIR /app

COPY . /src/

RUN cd /src && composer install --no-dev --optimize-autoloader --no-interaction
RUN /usr/local/bin/php /src/laracord app:build
RUN mv /src/builds/laracord .

ENTRYPOINT ["/entrypoint.sh"]
