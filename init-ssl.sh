#!/bin/bash
# Run once on the server to obtain the initial SSL certificate.
set -e

DOMAIN="videoflix.mohamed-touzani.de"
EMAIL="kontakt@mohamed-touzani.de"

echo "==> Step 1: Starting nginx with temporary HTTP-only config..."

# Temporarily replace nginx config with HTTP-only version so nginx can start
# without needing the SSL certs (which don't exist yet).
cp nginx/default.conf nginx/default.conf.bak

cat > nginx/default.conf << 'NGINXEOF'
server {
    listen 80;
    server_name videoflix.mohamed-touzani.de;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 200 'ok';
        add_header Content-Type text/plain;
    }
}
NGINXEOF

chmod +x backend.entrypoint.sh

docker compose -f docker-compose.prod.yml up -d nginx
sleep 5

echo "==> Step 2: Requesting SSL certificate from Let's Encrypt..."
docker compose -f docker-compose.prod.yml run --rm --entrypoint certbot certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email "$EMAIL" \
    --agree-tos \
    --no-eff-email \
    -d "$DOMAIN"

echo "==> Step 3: Restoring production nginx config with HTTPS..."
cp nginx/default.conf.bak nginx/default.conf
rm nginx/default.conf.bak

docker compose -f docker-compose.prod.yml exec nginx nginx -s reload

echo "==> Step 4: Starting all services..."
docker compose -f docker-compose.prod.yml up -d

echo ""
echo "Done! Backend is live at https://$DOMAIN"
