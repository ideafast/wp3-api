# IDEA-FAST WP3 Public Facing API

A public facing API used to feed the IDEA-FAST Study Dashboard. It includes some functionality embedded in the `IDEAFAST/middleware-service:consumer` repository, but has been started from scratch to interface with the `IDEAFAST/ideafast-etl` pipeline and newly set up Dashboard for simplicity and separation of tasks.

> The development setup, folder structure, and cli.py share a lot of commonalities with the `IDEAFAST/ideafast-etl` repository.

## Run the API Locally

### Setup

Rename the `.env.example` to `.env` and update the variables/secrets as needed.

### CLI

[Poetry](https://python-poetry.org/) is used for dependency management during development and [pyenv](https://github.com/pyenv/pyenv) to manage python installations, so please install both on your local machine. We use python 3.8 by default, so please make sure this is installed via pyenv, e.g.

```shell
pyenv install 3.8.0 && pyenv global 3.8.0
```

Once done, clone the repo to your machine, install dependencies for this project, and quickstart the API which will watch for local changes _(useful for during development!)_:

```shell
poetry install
poetry run local
```

Open your browser and try out a few endpoints, e.g.
- http://localhost:8000/patients
- http://localhost:8000/docs
- http://localhost:8000/status

> Note that for the pipeline endpoint, the [`ideafast-etl`](https://github.com/ideafast/ideafast-etl) docker image also needs to be running, as access is only provided locally.

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


## Running remotely

The API is hosted on the [ideafast/stack](https://github.com/ideafast/stack) using a docker-compose.yml file. You can mimick this locally by writing a docker-compose file such as in the [example.docker-compose.yml](example.docker-compose.yml) file.
