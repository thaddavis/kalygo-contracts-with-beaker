# TLDR

This is a library of production-grade smart contracts built for the Algorand blockchain using the Beaker Framework.

## Concerning the tests directory

All tests are using the code in found in the modules folder as helper functions. The code in the modules folder aims to use as much dependency injection as possible and all the tests are designed to be ran with the pytest command.

## Useful commands

- poetry run deploy
- poetry run pytest
- poetry run compile_with_beaker
- python -m pytest -s
