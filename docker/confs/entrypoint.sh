#!/usr/bin/env bash

/app/laracord migrate
/usr/local/bin/php /src/laracord app:build
mv /src/builds/laracord /app/laracord
/usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
