# IDEA-FAST WP3 Public Facing API

A public facing API used to feed the IDEA-FAST Study Dashboard. It includes some functionality embedded in the `IDEAFAST/middleware-service:consumer` repository, but has been started from scratch to interface with the `IDEAFAST/ideafast-etl` pipeline and newly set up Dashboard for simplicity and separation of concerns.

The primary task fo the API is to feed the IDEAFAST Study Dashboard with

- information about enrolled participants (provided though the `UCAM` api),
- details about their (temporary) app logins,
- the status of the [IDEAFAST ETL pipeline](https://github.com/ideafast/ideafast-etl), and
- serving device documentation and FAQ pulled from a private GitHub repo.

## Run the API locally and remotely using Docker

By design, the API is containerised and can be easily deployed with a docker-compose as implemented for [ideafast/stack](https://github.com/ideafast/stack). As an image, it needs to be fed an `.env` file to authenticate with 3rd party services, and a `ssh key` to authenticate with the private GitHub repository to pull the latest documentation.

### Setup

1. Rename the `.env.example` to `.env` and update the variables/secrets as needed.
2. Get the `ssh keys` from your colleague and store then in the [ssh](ssh) folder in this repository. If you, however, need a new one:
    - Navigate into the [ssh](ssh) folder _(cd ssh)_
    - Generate a key with the command below. _Note that the `-N ''` parameter results in a ssh key **without** password, which is generally not advised, but useful in an non-interactive container application as this one. The `-f ed25519` parameter results in the key being generated in the folder you navigated to_.
        ```shell
        ssh-keygen -t ed25519 -f id_ed25519 -C "email@example.com" -N ''
        ```
    - Go to the GitHub repository hosting the documentation (in this case github.com/ideafast/ideafast-devicesupportdocs-web, as you can see from the [scripts/prestart.sh](scripts/prestart.sh) script), navigate to _Settings_ and _Deploy keys_ and add this key as a read-only key.

### Run

Only meant as an example, but you can run the API locally with the example docker-compose file in this repository:

```shell
docker-compose -f example.docker-compose.yml up
```

Open your browser and try out a few endpoints, e.g.
- http://localhost/patients
- http://localhost/patients/credentials/{participant_id}
- http://localhost/docs/axivity
- http://localhost/status

Trigger a pull for new docs for the GET /docs endpoint by running
```shell
curl -X POST -H "Content-Type: application/json" -d '{"sample":"dict"}' http://localhost/docs/update
```

When deploying this API remotely, please implement the appropriate safety protocol (e.g. basic authentication) for access. IDEAFAST uses a reverse proxy with [traefik](https://traefik.io/) and restricts access to the API (such as the endpoint above) with basic authentication.

Note that all endpoints have dependencies on other (spun up) services with potential passwords (see [.example.env](.example.env)):
- GET /patients on the UCAM API _(the first request can take a while due to the serverless architecture used by UCAM)_
- GET /status on the the [`ideafast-etl`](https://github.com/ideafast/ideafast-etl) service
- GET /docs on the private GitHub repository, for which the ssh key is needed

### Adding participant credentials to the database

Patient credentials are made accessible to study site staff via the study dashboard, and the dashboard receives them via our API. However, credentials must first be loaded into the mongo database. A script - insert_credentials.py - is provided for this purpose within the */insert_credentials* folder. This script must be paired with a .csv file of patient credentials which should be named *credentials.csv* and placed within the credentials subdirectory. This directory maps onto a directory of the same name and path within the container, so the .csv can be prepared after the container has been started.

Once you have started the container, you can enter it like:
```shell
docker exec -it wp3-api_api_1 bash
```

Type 'ls' to list the files within the directory you have entered and yu should see an insert_credentials folder. Navigate to *insert_credentials/credentials* and ensure that you have placed a credentials.csv file is located here, as described above. Then up one level and you will find the script which inserts those credentials into the Mongo database. This can be run like:
```shell
python insert_credentials.py
```
----

## Development and hot-reloading

A CLI command sets up the API locally to enable hot-reloading as code changes, something the docker setup prevents. Please follow the advised steps below for local development.

### Preparations

[Poetry](https://python-poetry.org/) is used for dependency management during development and [pyenv](https://github.com/pyenv/pyenv) to manage python installations, so please install both on your local machine. We use python 3.8 by default, so please make sure this is installed via pyenv, e.g.

```shell
pyenv install 3.8.0 && pyenv global 3.8.0
```
Add the required environmental variables in the `.env` file and quickstart the API which will watch for local changes. This will also spin up a docker container for the `mongodb` and patient credentials. Add the `--clean` command to auto-clean the docker volume when you shut down the API:

```shell
poetry install
poetry run local # --clean
```

#### GET /docs
The documentation endpoint relies on a private git repository that needs to be loaded into the docker container at boot. This is handled by the [preshart.sh](scripts/prestart.sh) script. Locally, however, running this script outside a docker container will interfere with your local git and ssh setup. Instead, download the (private) repo as a .zip and place it into the api/docs folder for local development and testing.

## Local development

When adding depencies in development, consider if these are for development or needed in production, then run with or without the `--dev` flag:
```shell
poetry add new-dependency
poetry add new-dependency --dev
```

> Note that `click` is a core dependency solely for using the CLI locally, but is actually not required for the Docker image deployment.

Before commiting, be sure to have pre-commit set up

```shell
poetry run pre-commit install
```

If you make substantial changes, consider bumping the repo's version, build a new Docker image and pushing it to hub.docker.com:

```shell
poetry run bump -b patch  # or minor, or major
poetry run build
poetry run publish
```

To check the current version of the Poetry package, local Git (_Git and Poetry are synced when using above `bump` command_) and Docker image (_only adopts the Poetry/Git version when actually built_), run:
```shell
poetry run version
```

### Running Tests, Type Checking, Linting and Code Formatting

[Nox](https://nox.thea.codes/) is used for automation and standardisation of tests, type hints, automatic code formatting, and linting. Any contribution needs to pass these tests before creating a Pull Request.

To run all these libraries:

    poetry run nox -r

Or individual checks by choosing one of the options from the list:

    poetry run nox -rs [tests, mypy, lint, black]
