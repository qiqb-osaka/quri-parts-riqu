# Contribution Guidelines

We are happy that you are interested in contributing to QURI Parts riqu!
Please read the following contribution guidelines.


## Issues

Issues are managed on [GitHub](https://github.com/qiqb-osaka/quri-parts-riqu/issues).
Please search existing issues before opening a new one.


## Development

We use [Poetry](https://python-poetry.org/) to manage dependencies and packaging.
Install the latest version and run `poetry install` to create a virtualenv and install dependencies.


### Linting and testing

We use following tools for linting and testing.
Please make sure to run those tools and check if your code passes them.
All commands can be run in the Poetry virtualenv by:

- Use `poetry run`: for example `poetry run black .`, or
- Activate the virtualenv by `poetry shell` and run the command.

#### Import formatting

```
poetry run isort .
```

#### Code formatting

```
poetry run black .
```

#### Document formatting

```
poetry run docformatter -i -r .
```

#### Linting

```
poetry run flake8
```

#### Type checking

```
poetry run mypy .
```

#### Testing

```
poetry run pytest
```

### Documentation

You can build documentation by:

```
cd docs
poetry run make html
# For live preview
poetry run make livehtml
```

### Continuous integration (CI)

Once you create a pull request, the above linting and testing are executed on GitHub Actions.
All the checks need to be passed before merging the pull request.
