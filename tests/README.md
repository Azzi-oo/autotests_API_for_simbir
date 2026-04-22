# API tests

Python 3.10 + `requests` + `pydantic` + `pytest` integration tests for the Go service
exposed at `http://localhost:8080`.

## Run the service

```bash
make run   # or: docker compose up --build -d
```

## Install dependencies

```bash
python3.10 -m venv .venv
source .venv/bin/activate
pip install -r tests/requirements.txt
```

## Run the tests

```bash
# sequential
pytest tests

# parallel (pytest-xdist)
pytest tests -n auto

# Allure report
pytest tests
allure serve allure-results
```

Override the target host with `BASE_URL`:

```bash
BASE_URL=http://localhost:8080 pytest tests
```
