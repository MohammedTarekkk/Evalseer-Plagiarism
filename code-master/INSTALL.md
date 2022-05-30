# Installation

## Prerequisites

### Install mitlm dependencies

Ubuntu/Debian:

```bash
sudo apt-get install libzmq-dev automake autoconf gfortran python-virtualenv
```

Fedora:

```bash
sudo yum install automake autoconf gcc-gfortran python-virtualenv
# the version of zeromq3-devel on Fedora 19+ does not include zmq.hpp.
# grab it directly from upstream and drop it in for now
sudo wget https://raw.github.com/zeromq/cppzmq/master/zmq.hpp \
    -O /usr/include/zmq.hpp
```

## Build and Install in a Virtual Environment

```
git submodule init
git submodule update --recursive --remote
virtualenv venv
source venv/bin/activate
pip install -e .
```

# Testing

From the repository root directory:

```bash
py.test
```

_or_:

```bash
uctest
```

(Defined after running `. source_this.sh`).


You will need some environment variables set (set to defaults if using
`source_this.sh`:

```bash
export ESTIMATENGRAM="/usr/local/bin/estimate-ngram"
export LD_LIBRARY_PATH="/usr/local/lib:$LD_LIBRARY_PATH"
```

# Running

```bash
export PATH="/path/to/unnaturalcode/unnaturalcode:$PATH"
python setup.py develop
uclearn /usr/lib/python2.7/*.py
uclearn /path/to/some/known-good-python.py
ucwrap /path/to/some/python.py
uccheck some.python.module
```

