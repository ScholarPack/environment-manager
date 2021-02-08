![Validate Build](https://github.com/ScholarPack/flask-environment-manager/workflows/Validate%20Build/badge.svg)

# Flask Environment Manager

A Flask environment manager for copying parameters from a source into the Flask app config, while also abiding by an override whitelist.

Currently, this packaged supports overriding the config from:
- `os.environ` via `OsEnvironmentManager`
- `AWS SSM` via `SsmEnvironmentManager`

# Installation
Install and update using `pip`:

```bash 
pip install -U flask-environment-manager
```

# Getting Started

Before using the Environment Manager, you must ensure the following is set up in your Flask app config:

- ENV_OVERRIDE_WHITELIST

Example
```python
{
    "ENV_OVERRIDE_WHITELIST": [
        "ENV_VAR_1",
        "ENV_VAR_2",
        "ENV_VAR_3",
        "ENV_VAR_4"
    ],
}
```

The keys stored in the whitelist will be the only keys updated in the config.

# Managers

## SSM Environment Manager

This manager can be imported with `from flask_environment_manager import SsmEnvironmentManager`

This manager requires the following to be definied in the Flask app config, in addition the the whitelist:

- AWS_SSM_ACCESS_KEY
- AWS_SSM_ACCESS_SECRET
- AWS_SSM_REGION

This manager will connect to AWS SSM and get parameters from a given path.

The following snippet will load all parameters nested under the `/directory` path (recursively).

```python
from flask_environment_manager import SsmEnvironmentManager
manager = SsmEnvironmentManager(app, "/directory")
manager.load_into_config()
```

It is important to note that parameters are stored as their final name in the path. For example, the parameter stored at `/directory/params/param` will be stored as `param`.

## OS Environment Manager

This manager can be imported with `from flask_environment_manager import OsEnvironmentManager`

This manager will use the `os.environ` keys and values to update the `app.config`

```python
from flask_environment_manager import OsEnvironmentManager
manager = OsEnvironmentManager(app)
manager.load_into_config()
```

# Developing
__The build pipeline requires your tests to pass and code to be formatted__

Make sure you have Python 3.x installed on your machine (use [pyenv](https://github.com/pyenv/pyenv)).

Install the dependencies with [pipenv](https://github.com/pypa/pipenv) (making sure to include dev and pre-release packages):

```bash
pipenv install --dev --pre
```

Configure your environment:

```bash
pipenv shell && export PYTHONPATH="$PWD"
```

Run the tests:

```bash
pytest
```

Or with logging:

```bash
pytest -s
```

Or tests with coverage:

```bash
pytest --cov=./
```

Format the code with [Black](https://github.com/psf/black):

```bash
black $PWD
```

# Releases
Cleanup the (.gitignored) `dist` folder (if you have one):

```bash
rm -rf dist
```

Notch up the version number in `setup.py` and build:

```bash
python3 setup.py sdist bdist_wheel
```

Push to PyPi (using the ScholarPack credentials when prompted)

```bash
python3 -m twine upload --repository-url https://upload.pypi.org/legacy/ dist/*
```

# Links
* Releases: https://pypi.org/project/flask-environment-manager/
* Code: https://github.com/ScholarPack/flask-environment-manager
