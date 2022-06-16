# Sitemap Detective

Sitemap Detective is a microsaas app for lead filtering. You give it a list of domains and keywords you want to look for in the domain's sitemap and on-page content. It gives a csv back indicating which domains matched your search criteria.

For example, A VC firm interested in losing lots of money could provide a list of startup domains and search for "web3" or "blockchain".

## Local Development

Create a `dev.env` file from `sample.env`

```
docker-compose -f docker-compose-dev.yml up --build
```

Flask server is at http://localhost:5050
Flower (Worker diagnostics) is at http://localhost:5555

## Test commands

SSH into the app, flower or worker container and run <br>
`pytest {path/module_name.py}` to test a module. <br>
Add the `-v` flag for verbose output or `-q` for less

### Test Shortcuts

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

## Production notes

- download and configure AWS CLI
- Create Docker image and push to ECR [link](https://docs.aws.amazon.com/AmazonECR/latest/userguide/repository-create.html)
- Run `docker buildx build -t --platform linux/amd64 sitemap-detective .`
- Run `docker compose --context myecscontext up`
