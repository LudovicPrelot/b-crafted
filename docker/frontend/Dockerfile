FROM debian:bookworm-slim

# Debian Bookworm, dépôt principal
RUN echo 'deb http://deb.debian.org/debian/ bookworm main non-free-firmware' > /etc/apt/sources.list
RUN echo 'deb-src http://deb.debian.org/debian/ bookworm main non-free-firmware' > /etc/apt/sources.list
 
# Debian Bookworm, mises à jour de sécurité
RUN echo 'deb http://deb.debian.org/debian-security/ bookworm-security main non-free-firmware' > /etc/apt/sources.list
RUN echo 'deb-src http://deb.debian.org/debian-security/ bookworm-security main non-free-firmware' > /etc/apt/sources.list
 
# Debian Bookworm, mises à jour "volatiles"
RUN echo 'deb http://deb.debian.org/debian/ bookworm-updates main non-free-firmware' > /etc/apt/sources.list
RUN echo 'deb-src http://deb.debian.org/debian/ bookworm-updates main non-free-firmware' > /etc/apt/sources.list

RUN apt-get update -y
RUN apt-get upgrade -y

RUN apt-get install ca-certificates apt-transport-https software-properties-common wget bash curl nano lsb-release gnupg2 locales apt-utils git unzip zip libpq-dev libicu-dev g++ libpng-dev libxml2-dev libzip-dev libonig-dev libxslt-dev cron -y

RUN curl -sL https://deb.nodesource.com/setup_lts.x | bash -
RUN apt-get install -y build-essential bash nginx nginx-extras nodejs

ENV TZ=Europe/Paris
RUN rm -rf /etc/nginx/sites-enabled/default

EXPOSE 80

# Use exec form for CMD to avoid shell form duplication (lint rule)
# Start nginx in the foreground so the container PID 1 remains nginx
CMD ["nginx", "-g", "daemon off;"]

COPY ./docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod 0755 /docker-entrypoint.sh

# Normalize line endings in case the file was created on Windows (CRLF).
# CRLF in the shebang can cause "no such file or directory" at runtime.
# Use sed to remove CR carriage returns; sed is available in Debian base.
RUN sed -i 's/\r$//' /docker-entrypoint.sh

# Use exec form for ENTRYPOINT to avoid mixing shell and exec forms
# The script uses `exec "$@"` to hand off to the CMD below
ENTRYPOINT ["/docker-entrypoint.sh"]