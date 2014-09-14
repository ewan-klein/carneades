"""
Carneades model of argumentation
================================

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

>>> arg1 = Argument(a, premises={negb}, weight=0.3)
>>> arg2 = Argument(negb, premises={e}, weight=0.6)
>>> arg3 = Argument(negb, premises={g})

>>> h = PropLiteral('h')
>>> i = PropLiteral('i', False)
>>> arg4 = Argument(a, premises={h, i}, exceptions={negb})

>>> args = [arg1, arg2, arg3, arg4]
>>> for arg in args:
...     print(arg)
[-b], ~[] => a, 0.3
[e], ~[] => -b, 0.6
[e], ~[] => -b, 1.0
[-i, h], ~[-b] => a, 1.0


Argument set
------------

>>> argset = ArgumentSet()
>>> v0 = argset.add_proposition(a)
Added proposition 'a' to graph
>>> argset.propset()
{a}
>>> v1 = argset.add_proposition(negb)
Added proposition '-b' to graph
>>> argset.propset() == {a, negb}
True
>>> v0 = argset.add_proposition(a)
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
--------------

>>> ps = ProofStandard()
>>> d = {intent: "beyond_reasonable_doubt"}
>>> ps.set_standard(intent="beyond_reasonable_doubt")

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
>>> weights = {}
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




>>> arg1 = Argument(murder, premises={kill, intent})
>>> arg2 = Argument(intent, premises={witness1}, exceptions={unreliable1})
>>> arg3 = Argument(neg_intent, premises={witness2}, exceptions={unreliable2})

>>> argset.add_argument(arg1)
Added proposition 'murder' to graph
Added proposition '-murder' to graph
Added proposition 'intent' to graph
Added proposition 'kill' to graph
>>> argset.add_argument(arg2, verbose=False)
>>> argset.add_argument(arg3, verbose=False)
>>> #argset.draw()

>>> assumptions = {kill, witness1, witness2, unreliable2}
>>> audience = Audience(assumptions, weights)
>>> caes = CAES(argset, audience, ps)


"""

from igraph import *
from collections import namedtuple

class PropLiteral(object):
    """
    Proposition literals have most of the properties of ordinary strings,
    except that the negation method is Boolean; i.e. 
    
    >>> a = PropLiteral('a')
    >>> a.negate().negate() == a
    True
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
        
        We create a copy of the current proposition and flip its polarity.
        """
        polarity = (not self.polarity)
        return PropLiteral(self._string, polarity=polarity)
    

    def __str__(self):
        """
        Override ``__str__()`` so that negation is realised as a prefix on the
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
    """
    An argument consists of a conclusion, a set of premises and a set of
    exceptions (both of which can be empty).
    """
    def __init__(self, conclusion, premises=set(), exceptions=set(), arg_id=None, weight=1.0):
        """        
        :param conclusion: :py:class:`PropLiteral`
        :param premises: set(:py:class:`PropLiteral`)
        :param exceptions: set(:py:class:`PropLiteral`)
        """

        self.conclusion = conclusion
        self.premises = premises
        self.exceptions = exceptions
        self.weight = weight



    def __str__(self):
        if len(self.premises) == 0:
            prems = "[]"
        else:
            prems = sorted(self.premises)
        if len(self.exceptions) == 0:
            excepts = "[]"
        else:
            excepts = sorted(self.exceptions)
        return "{}, ~{} => {}, {}".format(prems, excepts, self.conclusion, self.weight)


class ArgumentSet(object):
    """
    An ``ArgumentSet`` is modeled as a dependency graph where vertices represent
    the components of an argument. A vertex corresponding to the conclusion
    of an argument *A* will depend on the premises and exceptions in *A*.
    """
    def __init__(self):
        self.graph = Graph()
        self.graph.to_directed()
        self.arg_count = 0

    def propset(self):
        """
        The set of :py:class:`PropLiteral`\ s represented by the vertices in
        the graph.
        """
        g = self.graph
        props = set()
        try:
            props = {p for p in g.vs['prop']}
        except KeyError:
            pass
        return props

    def add_proposition(self, prop, verbose=True):        
        """
        Add a proposition to a graph if it is not already present as a vertex.
        
        :param prop: The proposition to be added to the graph.
        :type prop: :py:class:`PropLiteral`
        :return: The graph vertex corresponding to the proposition.
        :rtype: :py:class:`PropLiteral`
        :raises TypeError: if the input is not a :py:class:`PropLiteral`.
        """
        if isinstance(prop, PropLiteral):
            if prop in self.propset():
                if verbose:
                    print("Proposition '{}' is already in graph".format(prop))                                           
            else:
                #print("Adding a new prop {} to propset {}".format(prop, self.propset()))
                
                self.graph.add_vertex(prop=prop)
                if verbose:
                    print("Added proposition '{}' to graph".format(prop))
            return self.graph.vs.select(prop=prop)[0]                
                
        else:
            raise TypeError('Input {} should be PropLiteral'.format(prop))

    def add_argument(self, argument, verbose=True):
        """
        Add an argument to the graph.
        
        :parameter argument: The argument to be added to the graph.
        :type argument: :py:class:`Argument`
        """
        g = self.graph
        arg_id = 'arg{}'.format(self.arg_count)
        self.arg_count += 1
        
        conclusions = [argument.conclusion, argument.conclusion.negate()]     
        v_conclusions = [self.add_proposition(conc, verbose=verbose) for conc in conclusions]        
        v_premises = [self.add_proposition(prop, verbose=verbose) for prop in sorted(argument.premises)]
        v_exceptions = [self.add_proposition(prop, verbose=verbose) for prop in sorted(argument.exceptions)]
        v_targets = v_premises + v_exceptions
        edges = [(v_conc.index, target.index) for v_conc in v_conclusions for target in v_targets]
        g.add_edges(edges)
        for v_conc in v_conclusions:
            try:   
                g.es.select(_source=v_conc.index)['args'].append(arg_id)
            except KeyError:
                g.es.select(_source=v_conc.index)['args'] = [arg_id]
        
        


    def draw(self):
        """
        Visualise an :py:class:`ArgumentSet` as a labeled graph.
        """
        g = self.graph
        try:
            g.vs['label'] = g.vs['prop']
        except KeyError:
            pass
        try:
            g.es['label'] = g.es['args']
        except KeyError:
            pass        
        layout = g.layout_reingold_tilford()
        layout = g.layout_auto()
        plot(g, layout=layout, vertex_label_size=16, vertex_size=8, vertex_label_dist=-5, margin=30)



class ProofStandard(object):
    """
    Each proposition in a CAES is associated with a proof standard.
    """
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


Audience = namedtuple('Audience', ['assumptions', 'argweight'])
"""
An audience has assumptions about which premises hold and also
assigns weights to arguments.
"""



class CAES(object):
    """
    A class that represents a Carneades Argument Evaluation Structure (CAES).
    """
    def __init__(self, argset, audience, standard):
        """
        
        :type argset: :py:class:`ArgSet`
        :type audience: :py:object:`Audience`
        :type standard: :py:class:`ArgSet`
        """
        self.argset = argset
        self.assumptions = audience.assumptions
        self.weights = audience.argweight
        self.standard = standard
        
    def applicable(self, argument):
        """
        An argument is *applicable* in a CAES if it needs to be taken into account when evaluating the CAES.
        
        :parameter argument: The argument whose applicablility is being determined.
        :type argument: :py:class:`Argument`
        :rtype: Boolean
        """
##        return \
##        argument.premises.issubset(p for p in argument.premises if \
##                                (p in self.assumptions or \
##                                (p.negate() not in self.assumptions and self.acceptable(p)))) \
##        and \
##        argument.exceptions.issubset(e for e in argument.exceptions if \
##                                (e not in self.assumptions and \
##                                (e.negate() in self.assumptions or not self.acceptable(p))))
    
        b1 = all(p in self.assumptions or \
                 (p.negate() not in self.assumptions and self.acceptable(p)) for p in argument.premises)
        
        b2 = all(e not in self.assumptions and \
                 (e.negate() in self.assumptions or not self.acceptable(p)) for e in argument.exceptions)
        
        acceptability = lambda p: self.acceptable(p)
        
        return self._applicable(argument, acceptability)
                                  
    def _applicable(self, argument, acceptability):
        """
        An argument is *applicable* in a CAES if it needs to be taken into account when evaluating the CAES.
        
        :parameter argument: The argument whose applicablility is being determined.
        :type argument: :py:class:`Argument`
        :rtype: Boolean
        """
##        return \
##        argument.premises.issubset(p for p in argument.premises if \
##                                (p in self.assumptions or \
##                                (p.negate() not in self.assumptions and self.acceptable(p)))) \
##        and \
##        argument.exceptions.issubset(e for e in argument.exceptions if \
##                                (e not in self.assumptions and \
##                                (e.negate() in self.assumptions or not self.acceptable(p))))
    
        b1 = all(p in self.assumptions or \
                 (p.negate() not in self.assumptions and acceptability(p)) for p in argument.premises)
        
        b2 = all(e not in self.assumptions and \
                 (e.negate() in self.assumptions or not sacceptability(p)) for e in argument.exceptions)
        
        return b1 and b2
       
                
    
    def acceptable(self, proposition):
        """
        A conclusion is *acceptable* in a CAES if it can be arrived at under
        the relevant proof standards, given the beliefs of the audience.
        """
        
        return True
                
                



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
    g.es['arg'] = ['arg1']
    g.es['label'] = g.es['arg']
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

