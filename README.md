# Website Filter

## How to use docker-compose locally for testing

### To rebuild the images . Use `--no-cache` if you want to download everything again and start from scratch

```
docker-compose build --no-cache
```

### To bring up the services in detached mode

```
docker-compose up -d
```

### To shutdown service and clear out everything

```
docker-compose down --rmi all
```

### Handy command to restart just one container

```
docker-compose restart [container name]
```

### Other items:
