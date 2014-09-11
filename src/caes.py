"""
Implementation of the Carneades model of argumentation.

Construct some proposition literals.

>>> a = PropLiteral('a')
>>> b = PropLiteral('b', False)

>>> print(a)
a
>>> print(b)
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

>>> d = b.negate()
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



Construct some arguments.

>>> arg1 = Argument(a, premises={b}, weight=0.3)
>>> arg2 = Argument(b, premises={e}, weight=0.6)
>>> arg3 = Argument(b, premises={g})

>>> h = PropLiteral('h')
>>> i = PropLiteral('i', False)
>>> arg4 = Argument(a, premises={h, i}, exceptions={b})

>>> args = [arg1, arg2, arg3, arg4]
>>> for arg in args:
...     print(arg)
[b], ~[] => a, 0.3
[e], ~[] => b, 0.6
[e], ~[] => b, 1.0
[-i, h], ~[b] => a, 1.0

Argument set

>>> argset = ArgumentSet()
>>> argset.add_proposition(a)
Added proposition 'a' to graph
>>> argset.propset()
{a}
>>> argset.add_proposition(b)
Added proposition 'b' to graph
>>> argset.propset() == {a, b}
True
>>> argset.add_proposition(a)
Proposition 'a' is already in graph


>>> kill = PropLiteral('kill')
>>> intent = PropLiteral('intent')
>>> neg_intent = intent.negate()
>>> murder = PropLiteral('murder')
>>> witness1 = PropLiteral('witness1')
>>> unreliable1 = PropLiteral('unreliable1')
>>> witness2 = PropLiteral('witness2')
>>> unreliable2 = PropLiteral('unreliable2')

Proof standard

>>> ps = ProofStandard()
>>> d = {intent: "beyond_reasonable_doubt"}
>>> ps.set_standard(intent="beyond_reasonable_doubt")

CAES

>>> argset = ArgumentSet()
>>> weights = {}
>>> assumptions = {kill, witness1, witness2, unreliable2}
>>> caes = CAES(argset, assumptions, weights, ps)
>>> arg1 = Argument(murder, premises={kill, intent}, weight=0.8)
>>> arg2 = Argument(intent, premises={witness1}, exceptions={unreliable1}, weight=0.3)
>>> arg3 = Argument(neg_intent, premises={witness2}, exceptions={unreliable2}, weight=0.8)

>>> argset.add_argument(arg1)
Added proposition 'murder' to graph
Added proposition '-intent' to graph
Added proposition 'kill' to graph
>>> argset.add_argument(arg2, verbose=False)
>>> argset.add_argument(arg3, verbose=False)
>>> argset.draw()

"""

from igraph import *
from collections import defaultdict

class PropLiteral(object):
    """
    Proposition literals have most of the properties of ordinary strings,
    except that the negation method is Boolean; ie. a.negate().negate() == a.
    """
    def __init__(self, string, polarity=True):
        """
        Propositions are either positive or negative atoms.
        """
        self.polarity = polarity
        self._string = string


    def negate(self):
        """
        Negation of a proposition.
        """
        polarity = (not self.polarity)
        return PropLiteral(self._string, polarity=polarity)
    

    def __str__(self):
        """
        Override __str__ so that negation is realised as a prefix on the
        string.
        """
        if self.polarity:
            return self._string
        return "-" + self._string

    def __hash__(self):
        return self._string.__hash__()

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__str__() == other.__str__()
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        return self.__str__() < other.__str__()





class Argument(object):
    def __init__(self, conclusion, premises=set(), exceptions=set(), weight=1.0):
        """
        Propositions are either positive or negative atoms.

        :param conclusion: PropLiteral
        :param premises: set(PropLiteral)
        :param exceptions: set(PropLiteral)
        """

        self.conclusion = conclusion
        self.premises = premises
        self.exceptions = exceptions
        self.weight = weight



    def __str__(self):
        if len(self.premises) == 0:
            prems = "[]"
        else:
            #prems = sorted(self.premises, key= lambda prop: prop.string)
            prems = sorted(self.premises)
        if len(self.exceptions) == 0:
            excepts = "[]"
        else:
            #excepts = sorted(self.exceptions, key= lambda prop: prop.string)
            excepts = sorted(self.exceptions)
        return "{}, ~{} => {}, {}".format(prems, excepts, self.conclusion, self.weight)


class ArgumentSet(object):
    def __init__(self):
        self.graph = Graph()
        self.graph.to_directed()

    def propset(self):
        g = self.graph
        props = set()
        try:
            props = {p for p in g.vs['prop']}
        except KeyError:
            pass
        return props

    def add_proposition(self, prop, verbose=True):
        if isinstance(prop, PropLiteral):
            if prop in self.propset():
                print("Proposition '{}' is already in graph".format(prop))
                return False                                
            else:
                print("Adding a new prop {} to propset {}".format(prop, self.propset()))
                
                self.graph.add_vertex(prop=prop)
                #self.propset.add(prop)
                print("Added proposition '{}' to graph".format(prop))
                return True                
                
        else:
            raise AssertionError('Input {} should be PropLiteral'.format(prop))

    def add_argument(self, argument, verbose=True):
        g = self.graph
        conclusion = argument.conclusion
        self.add_proposition(conclusion, verbose=verbose)
        v_conc = g.vs.select(prop=conclusion)[0]
        newprops = set()
        for prop in sorted(argument.premises):            
            if self.add_proposition(prop, verbose=verbose):
                newprops.add(prop)
        v_new = [v for v in g.vs if v['prop'] in newprops]
        edges = [(v_conc.index, target.index) for target in v_new]
        g.add_edges(edges)
        


    def draw(self):
        g = self.graph
        g.vs['label'] = g.vs['prop']
        layout = g.layout_reingold_tilford()
        layout = g.layout_auto()
        plot(g, layout=layout, vertex_label_size=16, vertex_size=8, vertex_label_dist=-5, margin=30)



class ProofStandard(object):
    def __init__(self, default='scintilla'):
        self.proof_standards = ["scintilla", "preponderance",
                                "clear_and_convincing", "beyond_reasonable_doubt",
                                "dialectical_validity"]
        self.default = default
        self.config = defaultdict(lambda x: self.default)

    def set_standard(self, **propstandards):
        for v in propstandards.values():
            if v not in self.proof_standards:
                raise ValueError("{} is not a valid proof standard".format(v))
        self.config.update(propstandards)

    def assign_standard(self, prop):
        return self.config[prop]



class CAES(object):
    def __init__(self, argset, assumptions, weights, standard):
        self.argset = argset
        self.assumptions = assumptions
        self.weights = weights
        self.standard = standard



DOCTEST = True

def graph_test():

    g = Graph()
    g.to_directed()
    a = PropLiteral('kill')
    b = PropLiteral('intent', False)
    c = PropLiteral('murder')

    g.add_vertex(prop=a)
    g.add_vertex(prop=b)
    g.add_vertex(prop=c)
    g.vs['label'] = g.vs['prop']

    g.add_edges([(2, 0), (2, 1)])
    props = [p for p in g.vs['prop']]
    print(props)
    layout = g.layout_grid()
    layout = g.layout_auto()
    plot(g, layout=layout, vertex_label_size=16, vertex_size=8, vertex_label_dist=-5, margin=30)

if __name__ == '__main__':
    if DOCTEST:
        import doctest
        doctest.testmod(optionflags=doctest.NORMALIZE_WHITESPACE)
    else:
        graph_test()

