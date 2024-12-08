# 5G Latency Experiment

Report PDF Link : https://drive.google.com/file/d/19CAwjlnqSUinuZI2QP9-4olAmMOmhLGm/view?usp=sharing
Report Overleaf Link : https://www.overleaf.com/read/mgdrfzbytjkz#00db25
Video Link : https://drive.google.com/drive/folders/1wq9bkoJPoTmwmlFeB6ZIZpWj7OWt6BGJ?usp=sharing


## Statement of purpose

Purpose of this code is to:

1. Measure a networks data throughput depending on the client's position, by sending packets of different sizes to a server while using a set of different communication libraries
2. Generate plots from the recorded data

To take the measurements, a client-server architecture is used.
The packages functions are exposed as scripts.

## Architecture

- `communication` contains the implementations of the different communication libraries.
    - for each communication library `CommunicationInterface` is subclassed once
    - `CommunicationInterface` serves more as a namespace than as a real class, because it only has static methods and is not supposed to have member variables / state
- `eval` contains the code for the evaluation tool (which is implemented using [streamlit](https://streamlit.io/))

## Installation

- Requires: Python 3 <= 3.8.10
- Install `experiments5G` with pip3, via the following methods:
    - When cloned locally: `[sudo] pip3 install <path/to/cloned/repository>`
    - Directly from the git repository: `[sudo] pip3 install pip3 install git+https://git.ni.dfki.de/ctittel/experiments5G.git`

It's recommended to run the `pip3 install` command as root (with `sudo`), because only then the scripts in `scripts/` are installed as system CLI application.
The following assumes that you installed the python packages as root and that the scripts in the `scripts/` directory are in the `$PATH`.

## Usage

**Assumption**: `experiments5G` was installed as root and the scripts in `scripts/` are thus available as system-wide CLI applications (if `experiments5G` was installed without root you will have to find and execute the scripts from where they are located, but the usage should otherwise be the same)

### Running the server

0. Check out the possible parameters with `experiments5G_server --help`
1. Run `experiments5G_server <your params>`

### Running the client

0. Check out the possible parameters with `experiments5G_client --help`
0. Make sure `experiments5G_server` is running and reachable
1. Run `experiments5G_client <your params>`

### Using the evaluation tool

1. Run `experiments5G_eval`
2. Open `http://localhost:8502/` in the browser (should be opened automatically)
3. Follow the instructions in the evaluation tool

## License

[Licensed under the MIT License](LICENSE)
