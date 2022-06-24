#!/bin/bash
# WARNING: run with working directory as /spidey/backend

echo "Creating uwsgi ini file..."
echo "[uwsgi]
chdir=$PWD
wsgi-file=wsgi.py
callable=app
http=0.0.0.0:$1
need-app=true
lazy-apps=true
master=true
processes=2
threads=2
single-interpreter=true
die-on-term=true
procname-prefix-spaced=spidey
vacuum=true
pidfile=spidey.pid
worker-reload-mercy=5">uwsgi.ini


echo "Creating deployment script..."
echo "#!/bin/bash

cd $PWD
source env/bin/activate
if [ -f ./spidey.pid ]; then
    uwsgi --stop ./spidey.pid
    sleep 6
fi
uwsgi --ini uwsgi.ini --daemonize log.txt" > start_uwsgi.sh
chmod +x start_uwsgi.sh

echo "Creating cron reboot job..."
crontab -l | grep -v "@reboot $PWD/start_uwsgi.sh" | crontab -
(crontab -l ; echo "@reboot $PWD/start_uwsgi.sh") | crontab -

echo "Running deployment script..."
./start_uwsgi.sh
