# Sitemap Detective
https://sitemap-detective.herokuapp.com/

Sitemap Detective is a microsaas app for lead filtering. You give it a list of domains and keywords you want to look for in the domain's sitemap and on-page content. It gives a csv back indicating which domains matched your search criteria.

For example, A VC firm interested in losing lots of money could provide a list of startup domains and search for "web3" or "blockchain".

## Setup

Create a `dev.env` file from `sample.env`

1. Set up Virtual Environment and install dependencies

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Build local Docker image

`docker-compose -f docker-compose-dev.yml build`

3. Run `./start.sh`

It runs the worker and flower diagnostics locally on the host machine but uses Docker containers to run the flask app and redis. This is the best compromise I could do to simulate production conditions while keeping the ability to hot reload.

The root folder is also mounted into the container so your code changes apply automatically in the flask container as well.

Flask server is at http://localhost:5050
Flower (Worker diagnostics) is at http://localhost:5555

Use `./stop.sh` in a different terminal to shutdown everything.

## Development Flow

1. Write code (in docker container)

2. Update requirements (if applicable)
   `pip freeze -l > requirements.txt`

3. Create Production Env File
   a) Copy `.env` into `prod.env`
   b) Change `CONFIG_TYPE=config.ProductionConfig` and `FLASK_ENV=production` along
   c) Change other env vars (just google and sql_db_uri at the moment) to use production/cloud based versions

4. Build and run production containers with
   `docker-compose -f docker-compose-prod.yml up --build`
   Confirm it can still build and run apps a) without mounting volumes b) using gunicorn in front of flask

5. Run tests in production container
   SSH into the app, flower or worker container and run <br>
   `pytest {path/module_name.py}` to test a module. <br>
   Add the `-v` flag for verbose output or `-q` for less
   `pytest tests/unit/test_scraper.py`
   `pytest tests/functional/test_views.py`

6. Push to main branch (yes this is super monkey, will evolve to something more sophisticated later)

7. Manual or Triggered (TBD) Workflow to deploy

## Other Notes

To get the logs from a container use the following command:

```
docker-compose logs -f [container_name]
```
