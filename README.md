Web countdown
========================

# Installation

```
sudo apt install python3-venv

python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt
```


## Load talks

Copy *init_db.py.dist* to *init_db.py* and adapt it.

Load talks by running `python3 init_db.py`.


# Running development server

```
FLASK_ENV=development flask run
```

# Running (almost) production server

```
flask run --host=0.0.0.0
```