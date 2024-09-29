#!/usr/bin/env bash

cp /app/.env /src/.env
/usr/local/bin/php /src/laracord app:build --build-version=unreleased
mv /src/builds/laracord /app/laracord
/app/laracord migrate
/usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
