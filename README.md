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

## Test commmands

`pytest {path/module_name.py}` to test a module
add the `-v` flag for more verbosity or `-q` for less

### Shortcuts

`pytest tests/unit/test_scraper.py`
`pytest tests/functional/test_views.py`
