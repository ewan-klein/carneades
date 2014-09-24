Carneades sample code
=====================

This is a pedagogically-oriented attempt to implement aspects of the [Carneades Argument Evaluation framework](http://carneades.github.io/carneades/Carneades/).  It closely follows the Haskell implementation in the [CarneadesDSL package](https://hackage.haskell.org/package/CarneadesDSL).

Requirements
------------

* Python3.4
* igraph
* Virtualenv (Optional)
* Sphinx (docs only)
* Basicstrap theme for sphinx (docs only)

Installation
------------

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
