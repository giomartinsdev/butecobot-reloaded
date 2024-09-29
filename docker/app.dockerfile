FROM brunofunnie/butecobot-reloaded-php:latest

WORKDIR /app

COPY . src/

RUN cd src && composer install --no-dev --optimize-autoloader --no-interaction
RUN cd src && php laracord app:build
RUN mv src/builds/laracord .

ENTRYPOINT ["/entrypoint.sh"]
