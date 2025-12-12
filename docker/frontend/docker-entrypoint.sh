#!/bin/bash
WWW="/var/www"
DIR="$WWW/app"
NPM_VERSION=11.6.4

echo "Installation npm $NPM_VERSION"
npm install -g npm@$NPM_VERSION
# Vérifiez la version de Node.js :
node -v # Doit afficher "v22.20.0".
# Vérifier la version de npm :
npm -v # Doit afficher "10.9.3".

if [ -d "$DIR" ]
then
	if [ "$(ls -A $DIR)" ]; then
    echo "Existing project"
	else
    echo "Non-existing project; creation"
    cd $WWW
    npx create-next-app@latest flowforge --ts --tailwind --no-linter --app --src-dir --turbopack --import-alias "@/*"
	fi
else
  mkdir -p $DIR
  chmod -R 0777 $DIR
  cd $WWW
  npx create-next-app@latest flowforge --ts --tailwind --no-linter --app --src-dir --turbopack --import-alias "@/*"
fi

cd $DIR
echo "Installation lucide-react"
npm install lucide-react
npm run dev

# Start cron
service cron start
# Hand off to the CMD
exec "$@"