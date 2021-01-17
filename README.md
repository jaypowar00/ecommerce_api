# ECom Django API

![ECom Build CI](https://github.com/StackUnderFlowHacks/ecommerce_api/workflows/ECom%20Test%20CI/badge.svg)
[![API URL](https://img.shields.io/badge/API-LINK-blueviolet)](https://shop-undrflw.herokuapp.com)

## How To Set Up Project Locally?

### Create & Activate Virtualenv

``` shell script
python3 -m venv venv
source venv/bin/activate
```

### Install Dependencies

``` shell script
pip install -r requirements.txt
```

### Add Database Settings

#### Create following environment variables :

```
    DB_NAME = <database name here> (default: postgres)
    DB_HOST_URL = <database url here> (default: localhost)
    DB_PORT = <database port here> (default: 5432)
    DB_USERNAME = <database username here> (default: postgres)
    DB_PASSWORD = <database password here> (default: password)
```

## Run Project

#### Do Migrations

``` shell script
python manage.py makemigrations
python manage.py migrate
```

#### Run Django server

``` shell script
python manage.py runserver
```
