# Introduction 
This project aim to serve as endpoint to the binpacking library, which will calculate the boxing of items.

# Build and Test
- Requires Python 3.9.
- Docker is recommended, although not mandatory.
- Requires binpacking lib to be in `src/libs/binpacking/`

### Install requirements with 
 - `pip install -r src/requirements.txt` on linux.
 - `pip install -r src/requirements-win.txt` on windows.

### Running
 - For development, run `python src/app.py`.
 - To run tests, run `run_tests.sh`.
 - In a linux production server, run `run.sh`.
 
### Get the tools for auth
The easiest way to use Python packages from the command line is with pip (19.2+) and the Azure Artifacts keyring.

Update pip
`python -m pip install --upgrade pip`

Install the keyring
`pip install keyring artifacts-keyring`

Install requirements (`pip install -R ...`)
