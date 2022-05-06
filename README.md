# Website Filter/Validator/ Name TBD

## Local Development Setup

Clone the repository, cd into it and run

```
docker-compose up -d --build
```

Test it out at http://localhost:5000. This project's root folder is mounted into the container so your code changes apply automatically.

To shutdown service use the flag `--rmi all` to clear everthing or just `-v` for the volumes

```
docker-compose down
```

## Production

```
docker-compose -f docker-compose.prod.yml up -d --build
```

### Other items:

```

```
