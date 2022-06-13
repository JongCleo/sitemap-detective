# Website Filter/Validator/ Name TBD

## Setup

Clone the repository, cd into it and run

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Then install my fork of the `ultimate-sitemap-parser` package

```
pip install -e git+https://github.com/JongCleo/ultimate-sitemap-parser#egg=ultimate-sitemap-parser
```

Then copy and fill `sample-env.env` into a `.env` at the project root.

## Local Development

run `./start.sh` from a bash terminal to start all services
and run `./stop.sh` to stop all services

Flask server is at http://localhost:5000
Flower (Worker diagnostics) is at http://localhost:5555

## Test commmands

`pytest {path/module_name.py}` to test a module
add the `-v` flag for more verbosity or `-q` for less

### Shortcuts

`pytest tests/unit/test_scraper.py`
`pytest tests/functional/test_views.py`

## Production Simulation

1. Copy your `.env` into a `prod.env`
2. Change `CONFIG_TYPE=config.ProductionConfig` and `FLASK_ENV=production` along
3. Change other env vars (just google and sql_db_uri at the moment) to use production/cloud based versions

To build fresh images and start containers:

```
docker-compose up -d --build
```

This project's root folder is mounted into the container so your code changes apply automatically.

To get the logs from a container use the following command:

```
docker-compose logs -f [container_name]
```

To shutdown service use the flag `--rmi all` to clear everthing or just `-v` for the volumes

```
docker-compose down
```
