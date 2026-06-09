Deployment steps

cd /var/www/myapp
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart
_______________________________________________________________________________
Setup


_______________________________________________________________________________
Firewall

ufw status

status: active

To                         Action      From
--                         ------      ----
OpenSSH                    ALLOW       Anywhere
Nginx Full                 ALLOW       Anywhere
OpenSSH (v6)               ALLOW       Anywhere (v6)
Nginx Full (v6)            ALLOW       Anywhere (v6)

________________________________________________________________________________
Nginx

server {
        listen 80;
        server_name skopjeparking.duckdns.org;

        location / {
        proxy_pass http://127.0.0.1:8000/;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        proxy_redirect off;
        }

    listen [::]:443 ssl ipv6only=on; # managed by Certbot
    listen 443 ssl; # managed by Certbot
    ssl_certificate /etc/letsencrypt/live/skopjeparking.duckdns.org/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/skopjeparking.duckdns.org/privkey.pem; # managed by Certbot
    include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot

}

server {
    if ($host = skopjeparking.duckdns.org) {
        return 301 https://$host$request_uri;
}

________________________________________________________________________________
Systemd parkingapp.service

[Unit]
Description=Gunicorn instance to serve Flask app
After=network.target

[Service]
User=viktor
Group=www-data
WorkingDirectory=/var/www/myapp

Environment="PATH=/var/www/myapp/venv/bin"
ExecStart=/var/www/myapp/venv/bin/gunicorn "run:create_app()" --workers 2 --bind 127.0.0.1:8000

Restart=always

[Install]
WantedBy=multi-user.target
