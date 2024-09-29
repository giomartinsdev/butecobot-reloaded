#!/usr/bin/env bash

cp /app/.env /src/.env
cd /src && /usr/local/bin/php laracord app:build --build-version=unreleased && mv builds/laracord /app/laracord
cd /app && /usr/local/bin/php /app/laracord migrate

/usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
