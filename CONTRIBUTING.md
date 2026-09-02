# Contributing to agentarchives

Thank you for your interest in making a contribution to agentarchives.

Since this project is used mostly in the general context of Archivematica, we
invite you to read the [Archivematica contributing guide](https://github.com/artefactual/archivematica/blob/qa/1.x/CONTRIBUTING.md)
to learn how to contribute to agentarchives.

Any information specific to the agentarchives project should be listed
below.

## Development workflows

Install uv using the [uv installation documentation], then synchronize the
locked project and development dependencies:

```bash
make sync
```

The Makefile exposes the common workflows:

- `make sync-runtime` installs only the project and runtime dependencies.
- `make sync` also installs development tools.
- `make lock-check` verifies that `uv.lock` matches `pyproject.toml`.
- `make lock` refreshes the lock without upgrading existing versions, while
  `make upgrade` upgrades all dependencies.
- `make check` verifies the lock and runs all pre-commit checks.
- `make test PYTEST_ARGS="..."` runs pytest with optional arguments.
- `make package-check` builds the sdist and wheel into `dist/` and validates
  them with twine; the release workflow runs the same target.

Declare runtime dependencies in `project.dependencies` and development
dependencies in `dependency-groups.dev` in `pyproject.toml`. The committed
`uv.lock` is the sole dependency lock; requirements exports are not
maintained.

The exact default interpreter is pinned in `.python-version`. Local uv commands
and the `setup-uv` GitHub Action discover it automatically. CI matrices
override this default to exercise every supported Python version. To upgrade
the default, update `.python-version` and run `make lock`. If the supported
range changes, also update `project.requires-python`, the classifiers and the
CI matrix.

`tool.uv.required-version` declares the minimum supported uv version and
accepts newer global installations. To raise it, update the value and run
`make lock` and `make check`.

The package version lives in `agentarchives/__init__.py`; release commits only need
to update `__version__` there. The lock does not record the project version.

[uv installation documentation]: https://docs.astral.sh/uv/getting-started/installation/
