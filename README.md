# Carneades sample code

This is a pedagogically-oriented attempt to implement aspects of the [Carneades Argument Evaluation framework](http://carneades.github.io/carneades/Carneades/).  It closely follows the Haskell implementation in the [CarneadesDSL package](https://hackage.haskell.org/package/CarneadesDSL).

## Requirements

* Python3.4
* igraph
* pycairo (for igraph)
* Virtualenv (Optional)
* Sphinx (docs only)
* Basicstrap theme for sphinx (docs only)

## Installation

### Install `python3.4` (via apt, homebrew or your favourite package_system)

Note for Linux users (especially Ubuntu 12.04 users): follow this
[link](#install-python34) to have more info about installing the
python distro.

### Create a virtualenv:

```bash
$ virtualenv -p python3.4 envname
$ source /envname/bin/activate
```

### Install sphinx and basicstrap

```bash
$ pip install sphinx
$ pip install sphinxjp.themes.basicstrap
```

### Install igraph

```bash
$ pip install python-igraph
```

This should also install the C bindings. If that doesn't happen because of some error, it's likely to be one of the 
following problems:

* The header files for the python distribution are not installed. Look up `python-dev` or `python3.4-dev`

* You need to compile the C code from source: download it
[here](http://igraph.org/) and follow the instructions. In general you
should only need to follow the standard procedure:

```bash
$ ./configure
$ make
$ make install
```

### Install pycairo

On Ubuntu, check this [package](http://packages.ubuntu.com/search?keywords=python-cairo).

If you are using a virtualenv or you don't use Ubuntu, do the following:

* Download and extract the pycairo package in the virtualenv

```bash
$ curl http://cairographics.org/releases/pycairo-1.10.0.tar.bz2 -O
$ tar xvf pycairo-1.10.0.tar.bz2
$ cd pycairo-1.10.0/
```

* edit a file in the hidden .waf folder that the extraction has created. To do this, go into the folder and edit ./war<numbers>/waflib/Tools/python.py to call the python3.4-config directly.
```diff
    --- waflib/Tools/python.py.old  2014-08-01 14:36:23.750613874 +0000
    +++ waflib/Tools/python.py      2014-08-01 14:36:38.359627761 +0000
    @@ -169,7 +169,7 @@
                    conf.find_program('python-config-%s'%num,var='PYTHON_CONFIG',mandatory=False)
            includes=[]
            if conf.env.PYTHON_CONFIG:
    -               for incstr in conf.cmd_and_log(conf.env.PYTHON+[conf.env.PYTHON_CONFIG,'--includes']).strip().split():
    +               for incstr in conf.cmd_and_log([conf.env.PYTHON_CONFIG,'--includes']).strip().split():
                            if(incstr.startswith('-I')or incstr.startswith('/I')):
                                    incstr=incstr[2:]
                            if incstr not in includes:
```

* compile and install the package

```bash
$ ./waf configure --prefix=$VIRTUAL_ENV
$ ./waf build
$ ./waf install
```

### Clone repository

```bash
$ git clone https://github.com/ewan-klein/carneades.git
$ cd carneades
```

### Generate the documentation

```bash
$ cd doc
$ make html
```

### Test the software

```bash
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

*WARNING: Although unlikely, this might break your python2 installation,
so do it at your own risk or set up a VM*

Unless you want to build from source (In which case, kudos!), add
[this PPA](https://launchpad.net/~fkrull/+archive/ubuntu/deadsnakes)),
to your apt source list:

```bash
$ add-apt-repository ppa:fkrull/deadsnakes
$ apt-get update
```

then run:

```bash
$ apt-get install python3.4 python3.4-dev
```

Now follow the rest of the installation.
