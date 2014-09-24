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
Note for Linux users (especially Ubuntu 12.04 users): follow this [link](#Install igraph)
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

## Install igraph

(Linux users)
-------------

The following is to install igraph on Ubuntu 12.04 LTS. Other
distributions should do more or less the same. If you have a newer
installation of Ubuntu or derivatives, you can probably skip some
passages.

*WARNING: it might break your python2 installation, so do it at your
own risk or set up a VM*

First off, igraph has to be installed using pip3, which is not
available on Ubuntu 12.04.

Assuming you already have installed python 3.4 (otherwise, check out [this PPA](https://launchpad.net/~fkrull/+archive/ubuntu/deadsnakes)), do this:

```
$ easy_install3 pip
$ pip install python-igraph
```
If you want to revert to pip for python2, just do and `easy_install pip`.

If the installation of python-igraph does not go well, it's most likely because you haven't got the necessary C bindings, so look up how to install them (it's either compiling from source or using apt-get).

Once you have done that, create a virtualenv:
```
$ virtualenv -p python3.4 envname
```

and follow the rest of the installation.
