# Search-engine

### Setup 
```sh
$ git clone https://github.com/atran10TF/Search-engine.git
$ cd Search-engine
# create virtual environment
$ python3 -m venv env
```

```sh
# Linux: activate virtual environment
$ source env/bin/activate
# Windows: activate virtual environment
$ env\Scripts\activate
```

```sh
# Install dependencies
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
(env) $ python3 -m pip install uwsgi
```

### Run uWSGI REST API Server (port 5000)
```
(env) $ uwsgi --socket 0.0.0.0:5000 --protocol=http -w wsgi:app
```