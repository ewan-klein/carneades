Carneades sample code
=====================

This is a pedagogically-oriented attempt to implement aspects of the [Carneades Argument Evaluation framework](http://carneades.github.io/carneades/Carneades/).  It closely follows the Haskell implementation in the [CarneadesDSL package](https://hackage.haskell.org/package/CarneadesDSL).

## Requirements

* Python3.4
* igraph
* Virtualenv (Optional)
* Sphinx (docs only)
* Basicstrap theme for sphinx (docs only)

## Installation

* Install `python3.4` (via apt/homebrew/$package_system)

Note for Linux users (especially Ubuntu 12.04 users): follow this
[link](#install-python3.4) to have more info about installing the
python distro.

* create a virtualenv:

```
$ virtualenv -p python3.4 envname
$ source /envname/bin/activate
```

* install sphinx and basicstrap

```
$ pip install sphinx
$ pip install sphinxjp.themes.basicstrap
```

* install igraph

```
$ pip install python-igraph
```

This should also install the C bindings. If that doesn't happen because of some error, it's like one of those problems:

1) The header files for the python distribution are not installed. Look up `python-dev` or `python3.4-dev`

2) You need to compile the C code from source: download it
[here](http://igraph.org/) and follow the instructions. In general you
should only need to follow the standard procedure:

```
$ ./configure
$ make
$ make install
```

* Clone repository
```
$ git clone https://github.com/ewan-klein/carneades.git
$ cd carneades
```

* Generate the documentation
```
$ cd doc
$ make html
```

* Test the software
```
$ cd ../src # relative root is carneades/
$ python -i caes.py
```


## Install python3.4

(Linux users)
-------------

The following is to install python3.4 on Ubuntu 12.04 LTS. Other
distributions should do more or less the same. If you have a newer
installation of Ubuntu or derivatives, you can probably skip some
passages.

*WARNING: although unlikely it might break your python2 installation,
so do it at your own risk or set up a VM*

Unless you want to build from source (In which case, kudos!), add
[this PPA](https://launchpad.net/~fkrull/+archive/ubuntu/deadsnakes)),
to your apt source list:

```
$ add-apt-repository ppa:fkrull/deadsnakes
$ apt-get update
```

then run:

```
$ apt-get install python3.4 python3.4-dev
```

Now follow the rest of the installation.
