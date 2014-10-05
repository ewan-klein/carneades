"""
Tests for caes module.

Propositions
------------



Construct some proposition literals.

>>> a = PropLiteral('a')
>>> negb = PropLiteral('b', False)

>>> print(a)
a
>>> print(negb)
-b

Get the negation of `c`.

>>> c = a.negate()
>>> print(c)
-a
>>> a.negate()
-a
>>> a == a.negate()
False
>>> a == a.negate().negate()
True
>>> d = negb.negate()
>>> print(d)
b

>>> e = PropLiteral('e')
>>> g = PropLiteral('e')
>>> print(e == g)
True

>>> f = e.negate().negate()
>>> print(f)
e
>>> print(e == f)
True


Arguments
---------

Construct some arguments.

>>> arg1 = Argument(a, premises={negb})
>>> arg2 = Argument(negb, premises={e})
>>> arg3 = Argument(negb, premises={g})

>>> h = PropLiteral('h')
>>> i = PropLiteral('i', False)
>>> arg4 = Argument(a, premises={h, i}, exceptions={negb})

>>> args = [arg1, arg2, arg3, arg4]
>>> for arg in args:
...     print(arg)
[-b], ~[] => a
[e], ~[] => -b
[e], ~[] => -b
[-i, h], ~[-b] => a


Argument set
------------

>>> argset = ArgumentSet()
>>> v0 = argset.add_proposition(a)
>>> argset.propset()
{a}
>>> v1 = argset.add_proposition(negb)
>>> argset.propset() == {a, negb}
True
>>> v3 = argset.add_proposition(a)

>>> kill = PropLiteral('kill')
>>> intent = PropLiteral('intent')
>>> neg_intent = intent.negate()
>>> murder = PropLiteral('murder')
>>> witness1 = PropLiteral('witness1')
>>> unreliable1 = PropLiteral('unreliable1')
>>> witness2 = PropLiteral('witness2')
>>> unreliable2 = PropLiteral('unreliable2')


Proof standard
--------------


>>> standards = [(intent, "beyond_reasonable_doubt")]
>>> ps = ProofStandard(standards)

CAES
----

Applicable Arguments in a CAES
++++++++++++++++++++++++++++++



>>> a = PropLiteral('a')
>>> b = PropLiteral('b')
>>> c = PropLiteral('c')
>>> negb = b.negate()

>>> assumptions1 = {a}
>>> arg1 = Argument(c, premises={a, b})
>>> argset = ArgumentSet()
>>> weights = {arg1: 0.8, arg2: 0.3, arg3: 0.8}
>>> audience = Audience(assumptions1, weights)
>>> caes = CAES(argset, audience, ps)

Assume every prop is acceptable.

>>> acceptability = lambda p: True

>>> caes._applicable(arg1, acceptability)
True

>>> assumptions2 = {a, negb}
>>> arg1 = Argument(c, premises={a, b})
>>> argset = ArgumentSet()
>>> weights = {}
>>> audience = Audience(assumptions2, weights)
>>> caes = CAES(argset, audience, ps)
>>> caes._applicable(arg1, acceptability)
False

Vacuously true if there are no premises

>>> arg2 = Argument(c, premises=set())
>>> argset = ArgumentSet()
>>> weights = {}
>>> audience = Audience(assumptions1, weights)
>>> caes = CAES(argset, audience, ps)
>>> caes._applicable(arg2, acceptability)
True
"""

if __name__ == '__main__':
    import os, sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))    
    from carneades.caes import *
    from carneades.tracecalls import TraceCalls
    import doctest
    doctest.testmod(optionflags=doctest.NORMALIZE_WHITESPACE)