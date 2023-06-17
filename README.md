## Installation instructions

1 - Install pipenv:

```bash
pip install pipenv
```

2 - Initialize the virtual environment and install the dependencies:

```bash
pipenv install
```

3 - Start the server on port 80:

```bash
pipenv run flask run --reload --host=0.0.0.0 --port=80
```

## Docker compose instructions

1 - Copy the .env.example file to .env:

```bash
cp .env.example .env
```

2 - Start docker compose:

```bash
docker compose up
```