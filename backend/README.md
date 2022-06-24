# Spidey Backend

### Setup 
```sh
$ # create virtual environment
$ python3 -m venv env
$ # Linux: activate virtual environment
$ source env/bin/activate
$ # Windows: activate virtual environment
$ env\Scripts\activate
```

```sh
(env) $ # Install dependencies
(env) $ python3 -m pip install wheel
(env) $ python3 -m pip install -r requirements.txt
```

### Run Filter / Indexer
```sh
(env) $ python3 FilterMain.py
(env) $ python3 IndexerMain.py
```

### Run CLI Search Engine
```sh
(env) $ python3 QueryMain.py
```

### Run Development REST API Server
```sh
(env) $ python3 QueryMainRestApi.py
```

### Setup uWSGI REST API Server (port 5000)
```
(env) $ sudo ufw allow 5000
(env) $ sudo apt-get install cron
(env) $ python3 -m pip install uwsgi
```

### Run uWSGI REST API Server (port 5000)
```
(env) $ ./init_uwsgi.sh 5000
```

### Stop uWSGI REST API Server
```
(env) $ uwsgi --stop ./spidey.pid
```

### Disable uWSGI REST API Server
```
(env) $ crontab -l | grep -v "@reboot $PWD/start_uwsgi.sh" | crontab -
```