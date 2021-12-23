# IDEA-FAST WP3 Public Facing API

A public facing API used to feed the IDEA-FAST Study Dashboard. It includes some functionality embedded in the `IDEAFAST/middleware-service 'consumer'` repository, but has been started from scratch to interface with the `IDEAFAST/ideafast-etl` pipeline and newly set up Dashboard for simplicity and separation of tasks.

> The development setup, folder structure, and cli.py share a lot of commonalities with the `IDEAFAST/ideafast-etl` repository.

## Local development

[Poetry](https://python-poetry.org/) is used for dependency management during development and [pyenv](https://github.com/pyenv/pyenv) to manage python installations, so please install both on your local machine. We use python 3.8 by default, so please make sure this is installed via pyenv, e.g.

```shell
pyenv install 3.8.0 && pyenv global 3.8.0
```

Once done, clone the repo to your machine and install dependencies for this project via:

```shell
poetry install
poetry run pre-commit install
```

> Note that `click` is a core dependency solely for using the CLI locally, but is actually not required for the Docker image deployment.

When adding depencies in development, consider if these are for development or needed in production, then run with or without the `--dev` flag:
```shell
poetry add new-dependency
poetry add new-dependency --dev
```

Then, initiate a virtual environment to use those dependencies, running:

```shell
poetry shell
```

### Develop
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
