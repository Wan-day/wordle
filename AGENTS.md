# AGENTS.md


## Project

This repo is created to replicate the game wordle using the python programming language and kivy framework for gui.


## Layout

- src/: main python files

## Conventions

- Language and version: Python 3.14 with type hints
- Error handling rule: return errors, do not throw across module boundaries
- Naming rule: follow flake8 and mypy standard
- Match the style of the file you are editing over any general preference.
- Add or update a test for every behavior change.

## Boundaries

Always:
- Read a file before you edit it.
- Keep changes to what the task asks for; mention other problems you notice instead of fixing them.

Ask first:
- Adding a dependency.
- Changing a public API, a database schema, or CI configuration.
- Deleting files.

Never:
- Commit secrets, or read `.env` files and credentials.
- Push to `main`, force-push, or rewrite history.
- Edit generated files: `<dist/, *.lock, src/generated/>`. Change the generator instead.

## More detail, loaded only when needed

- Architecture: `<docs/architecture.md>`
- Release process: `<docs/releasing.md>`
- <Subdirectory rules live in their own AGENTS.md, e.g. `packages/web/AGENTS.md`; the closest file to the code wins.>
