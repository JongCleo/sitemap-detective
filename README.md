# Website Filter/Validator/ Name TBD

## Setup

Clone the repository, cd into it and run

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Local Development

run `./start.sh` from a bash terminal to start all services
and run `./stop.sh` to stop all services

Flask server is at http://localhost:5000
Flower (Worker diagnostics) is at http://localhost:5555

## Maybe Later:

### Local Development Setup

Clone the repository, cd into it and run

```
docker-compose up -d --build
```

Test it out at http://localhost:5000. This project's root folder is mounted into the container so your code changes apply automatically.

To get the logs from a container use the following command:

```
docker-compose logs -f [container_name]
```

To shutdown service use the flag `--rmi all` to clear everthing or just `-v` for the volumes

```
docker-compose down
```

### Production

```
docker-compose -f docker-compose.prod.yml up -d --build
```
