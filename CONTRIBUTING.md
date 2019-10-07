## Starting Development

```bash
git clone git@github.com:dutradda/apidaora.git --recursive
cd apidaora
make setup-python-virtualenv
source venv/bin/activate
make setup-python-project
bake setup-apidaora
bake dependencies
```

## Running the integration suite:

```bash
bake integration
```

## Other bake tasks:

```bash
bake check-code

bake tests-docs

bake serve-docs

bake add-changelog m="Add my cool feature"
```

You can run `bake` to see all tasks available.
