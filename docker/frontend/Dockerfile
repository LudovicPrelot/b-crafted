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

CMD service nginx -g "daemon off;"

COPY ./docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod -R 0777 /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh
ENTRYPOINT ["/docker-entrypoint.sh"]