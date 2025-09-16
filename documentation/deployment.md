# Deployment & Configuration Guide

## Overview

This guide covers deploying the Nockpoint Archery Club Management System in various environments, from development to production.

## System Requirements

### Minimum Requirements
- **Python**: 3.8 or higher (recommended: 3.12)
- **Database**: SQLite (development) or PostgreSQL 12+ (production)
- **Memory**: 512MB RAM (minimum), 2GB+ recommended for production
- **Storage**: 1GB minimum for application and database
- **Web Server**: Built-in Flask server (development) or Gunicorn/uWSGI (production)

### Recommended Production Environment
- **OS**: Ubuntu 20.04 LTS or CentOS 8+
- **Python**: 3.12 with virtual environment
- **Database**: PostgreSQL 14+
- **Web Server**: Nginx + Gunicorn
- **Process Manager**: systemd or supervisor
- **SSL**: Let's Encrypt or commercial certificate
- **Monitoring**: Application and system monitoring tools

## Environment Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Flask Configuration
SECRET_KEY=your-secret-key-here
FLASK_ENV=production
FLASK_DEBUG=False

# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/nockpoint_db
# For development with SQLite:
# DATABASE_URL=sqlite:///instance/nockpoint.db

# Security Settings
WTF_CSRF_ENABLED=True
WTF_CSRF_TIME_LIMIT=3600

# Email Configuration (optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Application Settings
ITEMS_PER_PAGE=20
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216  # 16MB max file upload

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/nockpoint.log
```

### Configuration Classes

```python
# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///nockpoint.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = os.environ.get('WTF_CSRF_ENABLED', 'True').lower() == 'true'
    
class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or 'sqlite:///nockpoint_dev.db'

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
```

## Development Setup

### Local Development Environment

```bash
# Clone repository
git clone https://github.com/your-org/nockpoint.git
cd nockpoint

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Initialize database
flask db upgrade

# Create admin user
python -c "
from app import create_app, db
from app.models import User
app = create_app()
with app.app_context():
    admin = User(
        username='admin',
        email='admin@example.com',
        first_name='Admin',
        last_name='User',
        role='admin'
    )
    admin.set_password('admin')
    db.session.add(admin)
    db.session.commit()
    print('Admin user created: admin/admin')
"

# Run development server
python app.py
# Or: flask run --host=0.0.0.0 --port=5000
```

### Development with Docker

```dockerfile
# Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create logs directory
RUN mkdir -p logs

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://nockpoint:password@db:5432/nockpoint_db
      - SECRET_KEY=your-secret-key-here
    depends_on:
      - db
    volumes:
      - ./logs:/app/logs
      - ./uploads:/app/uploads

  db:
    image: postgres:14
    environment:
      POSTGRES_DB: nockpoint_db
      POSTGRES_USER: nockpoint
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

## Production Deployment

### 1. Server Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3 python3-venv python3-pip nginx postgresql postgresql-contrib supervisor certbot python3-certbot-nginx

# Create application user
sudo useradd -m -s /bin/bash nockpoint
sudo usermod -aG sudo nockpoint

# Switch to application user
sudo su - nockpoint
```

### 2. Database Setup

```bash
# Start and enable PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres psql << EOF
CREATE DATABASE nockpoint_db;
CREATE USER nockpoint WITH ENCRYPTED PASSWORD 'secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE nockpoint_db TO nockpoint;
ALTER USER nockpoint CREATEDB;  -- For running migrations
\q
EOF
```

### 3. Application Deployment

```bash
# Clone application
cd /opt
sudo git clone https://github.com/your-org/nockpoint.git
sudo chown -R nockpoint:nockpoint nockpoint
cd nockpoint

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn psycopg2-binary

# Set up environment
sudo cp .env.example .env
sudo nano .env  # Configure production settings

# Create necessary directories
mkdir -p logs uploads instance
sudo chown -R nockpoint:nockpoint logs uploads instance

# Run database migrations
export FLASK_APP=app.py
flask db upgrade

# Create admin user (optional)
python create_admin.py
```

### 4. Gunicorn Configuration

```bash
# /opt/nockpoint/gunicorn_config.py
bind = "127.0.0.1:5000"
workers = 3
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
user = "nockpoint"
group = "nockpoint"
tmp_upload_dir = None
max_requests = 1000
max_requests_jitter = 50
preload_app = True

# Logging
accesslog = "/opt/nockpoint/logs/gunicorn_access.log"
errorlog = "/opt/nockpoint/logs/gunicorn_error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'
```

### 5. Systemd Service

```bash
# /etc/systemd/system/nockpoint.service
[Unit]
Description=Nockpoint Archery Club Management System
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=notify
User=nockpoint
Group=nockpoint
RuntimeDirectory=nockpoint
WorkingDirectory=/opt/nockpoint
Environment=PATH=/opt/nockpoint/venv/bin
EnvironmentFile=/opt/nockpoint/.env
ExecStart=/opt/nockpoint/venv/bin/gunicorn --config /opt/nockpoint/gunicorn_config.py app:app
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable nockpoint
sudo systemctl start nockpoint
sudo systemctl status nockpoint
```

### 6. Nginx Configuration

```bash
# /etc/nginx/sites-available/nockpoint
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    # Static files
    location /static/ {
        alias /opt/nockpoint/app/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Uploads
    location /uploads/ {
        alias /opt/nockpoint/uploads/;
        expires 30d;
        add_header Cache-Control "public";
    }

    # Application
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # Timeouts
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    # File upload size limit
    client_max_body_size 16M;
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/nockpoint /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 7. SSL Certificate

```bash
# Install SSL certificate with Certbot
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

## Database Management

### Backup Strategy

```bash
# /opt/nockpoint/scripts/backup_db.sh
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/nockpoint/backups"
DB_NAME="nockpoint_db"
DB_USER="nockpoint"

mkdir -p $BACKUP_DIR

# Create database backup
pg_dump -U $DB_USER -h localhost $DB_NAME > $BACKUP_DIR/nockpoint_$DATE.sql

# Compress backup
gzip $BACKUP_DIR/nockpoint_$DATE.sql

# Keep only last 30 days of backups
find $BACKUP_DIR -name "nockpoint_*.sql.gz" -mtime +30 -delete

echo "Backup completed: nockpoint_$DATE.sql.gz"
```

```bash
# Add to crontab for daily backups
sudo crontab -e
# Add line: 0 2 * * * /opt/nockpoint/scripts/backup_db.sh
```

### Database Migrations

```bash
# Create migration
flask db migrate -m "Description of changes"

# Review migration file
# Edit migrations/versions/xxx_description.py if needed

# Apply migration
flask db upgrade

# Rollback if needed
flask db downgrade
```

## Monitoring & Logging

### Application Logging

```python
# app/logging_config.py
import logging
import logging.handlers
import os

def setup_logging(app):
    if not app.debug:
        log_level = getattr(logging, os.environ.get('LOG_LEVEL', 'INFO').upper())
        
        # File handler
        log_file = os.environ.get('LOG_FILE', 'logs/nockpoint.log')
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=10240000, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(log_level)
        
        app.logger.addHandler(file_handler)
        app.logger.setLevel(log_level)
        app.logger.info('Nockpoint startup')
```

### System Monitoring

```bash
# Install monitoring tools
sudo apt install -y htop iotop nethogs

# Monitor application
sudo systemctl status nockpoint
sudo journalctl -u nockpoint -f

# Monitor nginx
sudo systemctl status nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Monitor database
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity WHERE state = 'active';"
```

## Performance Optimization

### Database Optimization

```sql
-- Add indexes for better performance
CREATE INDEX idx_competition_registration_member ON competition_registration(member_id);
CREATE INDEX idx_arrow_score_registration ON arrow_score(registration_id);
CREATE INDEX idx_event_attendance_event ON event_attendance(event_id);
CREATE INDEX idx_event_attendance_member ON event_attendance(member_id);
CREATE INDEX idx_shooting_event_date ON shooting_event(date);
```

### Caching Configuration

```python
# app/cache_config.py
from flask_caching import Cache

cache = Cache()

def init_cache(app):
    cache_config = {
        'CACHE_TYPE': 'simple',  # Use Redis in production
        'CACHE_DEFAULT_TIMEOUT': 300
    }
    cache.init_app(app, config=cache_config)
    return cache

# Usage in views
@cache.cached(timeout=300, key_prefix='competitions_list')
def get_competitions_list():
    # Expensive database query
    pass
```

## Security Hardening

### Server Security

```bash
# Firewall configuration
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

# Disable unused services
sudo systemctl disable apache2  # if installed
sudo systemctl stop apache2

# Update system packages regularly
sudo apt update && sudo apt upgrade -y

# Configure automatic security updates
sudo apt install unattended-upgrades
sudo dpkg-reconfigure unattended-upgrades
```

### Application Security

```python
# Security configuration
SECURITY_HEADERS = {
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'SAMEORIGIN',
    'X-XSS-Protection': '1; mode=block',
    'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';"
}

@app.after_request
def set_security_headers(response):
    for header, value in SECURITY_HEADERS.items():
        response.headers[header] = value
    return response
```

## Troubleshooting

### Common Issues

#### Database Connection Issues
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check database connectivity
sudo -u nockpoint psql -h localhost -U nockpoint nockpoint_db -c "SELECT 1;"

# Check connection limits
sudo -u postgres psql -c "SHOW max_connections;"
sudo -u postgres psql -c "SELECT count(*) FROM pg_stat_activity;"
```

#### Application Not Starting
```bash
# Check service logs
sudo journalctl -u nockpoint -n 50

# Check Python errors
cd /opt/nockpoint
source venv/bin/activate
python app.py  # Run directly to see errors

# Check file permissions
ls -la /opt/nockpoint/
sudo chown -R nockpoint:nockpoint /opt/nockpoint/
```

#### High Memory Usage
```bash
# Monitor memory usage
htop
free -h

# Adjust gunicorn workers
sudo nano /opt/nockpoint/gunicorn_config.py
# Reduce workers if memory is limited

sudo systemctl restart nockpoint
```

### Performance Issues

#### Slow Database Queries
```sql
-- Enable query logging
ALTER SYSTEM SET log_statement = 'all';
ALTER SYSTEM SET log_min_duration_statement = 1000;  -- Log queries > 1 second
SELECT pg_reload_conf();

-- Analyze slow queries
SELECT query, mean_time, calls FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;
```

#### High CPU Usage
```bash
# Monitor processes
htop
sudo iotop

# Profile Python application
pip install py-spy
sudo py-spy record -o profile.svg -d 30 -p $(pgrep -f gunicorn)
```

## Maintenance Procedures

### Regular Maintenance Tasks

```bash
# /opt/nockpoint/scripts/maintenance.sh
#!/bin/bash

# Backup database
/opt/nockpoint/scripts/backup_db.sh

# Clean old log files
find /opt/nockpoint/logs -name "*.log.*" -mtime +30 -delete

# Clean old uploads (if applicable)
find /opt/nockpoint/uploads -name "*.tmp" -mtime +1 -delete

# Update system packages
sudo apt update && sudo apt upgrade -y

# Restart services if needed
if [ -f /var/run/reboot-required ]; then
    echo "System reboot required"
    # sudo reboot  # Uncomment for automatic reboot
fi
```

### Update Procedure

```bash
# 1. Backup current installation
sudo cp -r /opt/nockpoint /opt/nockpoint_backup_$(date +%Y%m%d)

# 2. Pull latest code
cd /opt/nockpoint
sudo git fetch origin
sudo git checkout main
sudo git pull origin main

# 3. Update dependencies
source venv/bin/activate
pip install -r requirements.txt

# 4. Run migrations
flask db upgrade

# 5. Restart services
sudo systemctl restart nockpoint
sudo systemctl reload nginx

# 6. Test application
curl -I https://your-domain.com
```
