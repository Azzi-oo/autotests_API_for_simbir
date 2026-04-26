# API tests

Python 3.10+ / `requests` / `pydantic` / `pytest` интеграционные тесты
Go-сервиса на `http://localhost:8080`.

## Архитектура

```
tests/
├── conftest.py             
├── pytest.ini              
├── core/                    
│   ├── api_client.py        
│   ├── models.py            
│   ├── builders.py          
│   └── assertions.py        
├── positive/                
│   ├── test_create.py
│   ├── test_read.py
│   ├── test_update.py
│   └── test_delete.py
└── negative/                
    ├── test_not_found.py
    └── test_invalid_input.py
```

## Запуск сервиса

```bash
make run   # или: docker compose up --build -d
```

## Установка зависимостей

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r tests/requirements.txt
```

## Запуск тестов

```bash
# всё
pytest tests

pytest tests -m positive
pytest tests -m negative

pytest tests -n auto

pytest tests
allure serve allure-results
```

Адрес сервиса переопределяется переменной `BASE_URL`:

```bash
BASE_URL=http://localhost:8080 pytest tests
```
