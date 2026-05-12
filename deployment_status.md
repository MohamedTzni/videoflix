# Deployment Status — videoflix.mohamed-touzani.de

## Server
- **VPS:** IONOS Ubuntu 24.04, IP `217.154.174.108`
- **Domain:** `videoflix.mohamed-touzani.de` → A-Record auf VPS-IP gesetzt
- **SSL:** Let's Encrypt Zertifikat, gültig bis 10.08.2026, Auto-Renewal aktiv

---

## Erledigt

### Backend
- [x] Django + Gunicorn läuft in Docker (`videoflix_backend`)
- [x] PostgreSQL läuft in Docker (`videoflix_database`)
- [x] Redis läuft in Docker (`videoflix_redis`)
- [x] RQ Worker für Video-Konvertierung aktiv
- [x] Migrationen, Static Files, Superuser-Erstellung laufen automatisch beim Start
- [x] `.env` auf dem Server konfiguriert (Produktion)
- [x] `DEBUG=False`, `JWT_COOKIE_SECURE=True`

### Nginx & SSL
- [x] Nginx läuft in Docker (`videoflix_nginx`)
- [x] HTTP → HTTPS Redirect aktiv
- [x] Certbot läuft in Docker (`videoflix_certbot`), erneuert alle 12h
- [x] Host-Nginx deaktiviert (`systemctl disable nginx`)

### Frontend
- [x] Frontend-Repo geklont nach `/var/www/frontend`
- [x] Nginx liefert Frontend unter `/` aus
- [x] `API_BASE_URL` auf `https://videoflix.mohamed-touzani.de/api/` gesetzt

---

## Noch offen / Bekannte Probleme

### .env auf dem Server unvollständig
Beim Erstellen der `.env` per `cat > .env << 'EOF'` wurden die letzten Zeilen abgeschnitten.
Folgende Variablen fehlen möglicherweise:
```
EMAIL_USE_SSL=False
DEFAULT_FROM_EMAIL=kontakt@mohamed-touzani.de
JWT_COOKIE_SECURE=True
JWT_COOKIE_SAMESITE=Lax
```
→ Prüfen mit: `cat ~/videoflix-backend/.env`
→ Falls fehlend: manuell nachtragen und Container neu starten:
```bash
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d
```

### E-Mail-Versand nicht getestet
- Registrierung wurde gestartet aber E-Mail-Zustellung noch nicht bestätigt
- IONOS SMTP: `smtp.ionos.de:587` mit `kontakt@mohamed-touzani.de`
- Falls keine E-Mail ankommt: IONOS-Postfach auf SMTP-Zugang prüfen

### config.js Änderung nicht persistent
Die `API_BASE_URL` wurde direkt auf dem Server mit `sed` geändert — **nicht im Git-Repo**.
Bei erneutem `git clone` oder `git pull` wird die Änderung überschrieben.
→ Fix: Änderung im Fork `MohamedTzni/project.Videoflix` committen.

### Frontend noch nicht mit echten Videos getestet
- Kein Video hochgeladen
- HLS-Streaming noch nicht getestet
- Admin-Panel: `https://videoflix.mohamed-touzani.de/admin/`

---

## Wichtige Befehle auf dem Server

```bash
# Alle Container starten
cd ~/videoflix-backend
docker compose -f docker-compose.prod.yml up -d

# Alle Container stoppen
docker compose -f docker-compose.prod.yml down

# Logs ansehen
docker logs videoflix_backend
docker logs videoflix_nginx

# Nach Code-Änderungen
git pull
docker compose -f docker-compose.prod.yml up -d --force-recreate web

# Frontend aktualisieren
cd /var/www/frontend
git pull
```

---

## Zugänge

| Was | Wo |
|---|---|
| Admin-Panel | https://videoflix.mohamed-touzani.de/admin/ |
| RQ Dashboard | https://videoflix.mohamed-touzani.de/django-rq/ |
| Frontend | https://videoflix.mohamed-touzani.de/ |
| SSH | `ssh root@217.154.174.108` |
