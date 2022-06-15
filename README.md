# Website Filter/Validator/ Name TBD

## Local Development

run `docker-compose -f docker-compose-dev.yml up --build`

Flask server is at http://localhost:5050
Flower (Worker diagnostics) is at http://localhost:5555

## Test commmands

SSH into the app, flower or worker container and run
`pytest {path/module_name.py}` to test a module
add the `-v` flag for more verbosity or `-q` for less

### Shortcuts

`pytest tests/unit/test_scraper.py`
`pytest tests/functional/test_views.py`

## Production Simulation

1. Copy `.env` into `prod.env`
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
