"""
Carneades model of argumentation
================================

>>> a = PropLiteral('a')
>>> argset = ArgumentSet()
>>> v = argset.add_proposition(a)

Using a CAES
++++++++++++

>>> kill = PropLiteral('kill')
>>> intent = PropLiteral('intent')
>>> neg_intent = intent.negate()
>>> murder = PropLiteral('murder')
>>> witness1 = PropLiteral('witness1')
>>> unreliable1 = PropLiteral('unreliable1')
>>> witness2 = PropLiteral('witness2')
>>> unreliable2 = PropLiteral('unreliable2')

>>> ps = ProofStandard(default='scintilla')
>>> #ps.set_standard(intent="beyond_reasonable_doubt")

>>> arg1 = Argument(murder, premises={kill, intent}, arg_id='arg1')
>>> arg2 = Argument(intent, premises={witness1}, exceptions={unreliable1}, arg_id='arg2')
>>> arg3 = Argument(neg_intent, premises={witness2}, exceptions={unreliable2}, arg_id='arg3')

>>> argset = ArgumentSet()
>>> argset.add_argument(arg1)
>>> argset.add_argument(arg2)
>>> argset.add_argument(arg3)
>>> #argset.draw()
>>> for a in argset.arguments_pro_and_con(murder): print(a)
[intent, kill], ~[] => murder
>>> for a in argset.arguments_pro_and_con(intent): print(a)
[witness1], ~[unreliable1] => intent
[witness2], ~[unreliable2] => -intent
    
>>> assumptions = {kill, witness1, witness2, unreliable2}
>>> weights = {'arg1': 0.8, 'arg2': 0.3, 'arg3': 0.8}
>>> audience = Audience(assumptions, weights)
>>> caes = CAES(argset, audience, ps)
>>> caes.applicable(arg1)
True
>>> caes.weight_of(arg2)
0.3
>>> caes.max_weight_applicable([arg1, arg2, arg3])
0.8
"""


from collections import namedtuple

import logging
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)

from igraph import *



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
    def __init__(self, conclusion, premises=set(), exceptions=set(), arg_id=None):
        """        
        :param conclusion: The conclusion of the argument.
        :type conclusion: :class:`PropLiteral`
        :param premises: The premises of the argument.
        :type premises: set(:class:`PropLiteral`)
        :param exceptions: The exceptions of the argument
        :type exceptions: set(:class:`PropLiteral`)
        :param arg_id: The exceptions of the argument
        :type arg_id: None or str
        :param weight: The exceptions of the argument
        :type arg_id: None or str
        
        """

        self.conclusion = conclusion
        self.premises = premises
        self.exceptions = exceptions
        self.arg_id = arg_id



    def __str__(self):
        if len(self.premises) == 0:
            prems = "[]"
        else:
            prems = sorted(self.premises)
        if len(self.exceptions) == 0:
            excepts = "[]"
        else:
            excepts = sorted(self.exceptions)
        return "{}, ~{} => {}".format(prems, excepts, self.conclusion)


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
        self.arguments = []

    def propset(self):
        """
        The set of :class:`PropLiteral`\ s represented by the vertices in
        the graph.
        """
        g = self.graph
        props = set()
        try:
            props = {p for p in g.vs['prop']}
        except KeyError:
            pass
        return props

    def add_proposition(self, proposition):        
        """
        Add a proposition to a graph if it is not already present as a vertex.
        
        :param prop: The proposition to be added to the graph.
        :type prop: :class:`PropLiteral`
        :return: The graph vertex corresponding to the proposition.
        :rtype: :class:`PropLiteral`
        :raises TypeError: if the input is not a :class:`PropLiteral`.
        """
        if isinstance(proposition, PropLiteral):
            if proposition in self.propset():
                logging.debug("Proposition '{}' is already in graph".format(proposition))                     
            else:
                self.graph.add_vertex(prop=proposition)
                logging.debug("Added proposition '{}' to graph".format(proposition))
            return self.graph.vs.select(prop=proposition)[0]                
                
        else:
            raise TypeError('Input {} should be PropLiteral'.format(proposition))

    def add_argument(self, argument):
        """
        Add an argument to the graph.
        
        :parameter argument: The argument to be added to the graph.
        :type argument: :class:`Argument`
        """
        g = self.graph
        arg_id = 'arg{}'.format(self.arg_count)
        if argument.arg_id is None:
            argument.arg_id = arg_id
        else:
            arg_id = argument.arg_id
        self.arg_count += 1
        self.arguments.append(argument)
        
        # add new vertices to the graph
        self.graph.add_vertex(arg=arg_id)
        arg_v = g.vs.select(arg=arg_id)[0]
        conclusions = [argument.conclusion, argument.conclusion.negate()]     
        conclusion_vs = [self.add_proposition(conc) for conc in conclusions]        
        premise_vs = [self.add_proposition(prop) for prop in sorted(argument.premises)]
        exception_vs = [self.add_proposition(prop) for prop in sorted(argument.exceptions)]
        target_vs = premise_vs + exception_vs
        
        # add new vertices to the graph
        edges_to_arg = [(conc_v.index, arg_v.index) for conc_v in conclusion_vs]
        edges_from_arg = [(arg_v.index, target.index) for target in target_vs]
        g.add_edges(edges_to_arg + edges_from_arg)
        
        
    def arguments_pro_and_con(self, proposition):
        """
        Find the arguments for a proposition in an *ArgumentSet*.
        
        :param proposition: The proposition to be checked.
        :type proposition: :class:`PropLiteral`
        :return: A list of the arguments pro the proposition
        :rtype: list(:class:`Argument`)
        """
        g = self.graph
        index_conc = g.vs.select(prop=proposition)[0].index
        v_targets = [e.target for e in g.es.select(_source=index_conc)]
        v_out = [g.vs[i] for i in v_targets]
        args = [v['arg'] for v in v_out]
        return [arg for arg in self.arguments if arg.arg_id in args]
        


    def draw(self):
        """
        Visualise an :class:`ArgumentSet` as a labeled graph.
        """
        g = self.graph
        labels = g.vs['prop']
        for i in range(len(labels)):
            if g.vs['arg'][i] is not None:
                labels[i] = g.vs['arg'][i]
        g.vs['label'] = labels
      
        
        roots = [i for i in range(len(g.vs)) if g.indegree()[i] == 0]
        layout = g.layout_reingold_tilford(mode=ALL, root=roots)

        plot_style = {}
        plot_style['vertex_color'] = ['lightblue' if x is None else 'pink' for x in g.vs['arg'] ]  
        plot_style['vertex_size'] = 60
        plot_style['vertex_shape'] = ['circle' if x is None else 'rect' for x in g.vs['arg'] ]      
        plot_style['margin'] = 40
        plot_style['layout'] = layout
        
        plot(g, **plot_style)



class ProofStandard(object):
    """
    Each proposition in a CAES is associated with a proof standard.
    """
    def __init__(self, default='scintilla'):
        self.proof_standards = ["scintilla", "preponderance",
                                "clear_and_convincing", "beyond_reasonable_doubt",
                                "dialectical_validity"]
        self.default = default
        self.config = defaultdict(lambda: self.default)

    def set_standard(self, **propstandards):
        for v in propstandards.values():
            if v not in self.proof_standards:
                raise ValueError("{} is not a valid proof standard".format(v))
        self.config.update(propstandards)

    def assign_standard(self, prop):
        return self.config[prop]


Audience = namedtuple('Audience', ['assumptions', 'weight'])
"""
An audience has assumptions about which premises hold and also
assigns weights to arguments.
"""



class CAES(object):
    """
    A class that represents a Carneades Argument Evaluation Structure (CAES).
 
    """
    def __init__(self, argset, audience, proofstandard):
        """
        
        :type argset: :class:`ArgSet`
        :type audience: :class:`Audience`
        :type standard: :class:`ProofStandard`
        """
        self.argset = argset
        self.assumptions = audience.assumptions
        self.weight = audience.weight
        self.standard = proofstandard
        
    def applicable(self, argument):
        """
        An argument is *applicable* in a CAES if it needs to be taken into account when evaluating the CAES.
        
        :parameter argument: The argument whose applicablility is being determined.
        :type argument: :class:`Argument`
        :rtype: bool
        """
        acceptability = lambda p: self.acceptable(p)        
        return self._applicable(argument, acceptability)
                                  
    def _applicable(self, argument, acceptability):
        """       
        :parameter argument: The argument whose applicablility is being determined.
        :type argument: :class:`Argument`
        :parameter acceptability: The function which determines the acceptability of a proposition in the CAES.
        :type acceptability: LambdaType
        :rtype: bool
        """
        logging.debug('Checking applicability of {}...'.format(argument.arg_id))
        logging.debug('Current assumptions: {}'.format(self.assumptions))
        logging.debug('Current premises: {}'.format(argument.premises))
        b1 = all(p in self.assumptions or \
                 (p.negate() not in self.assumptions and acceptability(p)) for p in argument.premises)
        
        if argument.exceptions:
            logging.debug('Current exception: {}'.format(argument.exceptions))
        b2 = all(e not in self.assumptions and \
                 (e.negate() in self.assumptions or not acceptability(e)) for e in argument.exceptions)
        
        return b1 and b2
       
                
    
    def acceptable(self, proposition):
        """
        A conclusion is *acceptable* in a CAES if it can be arrived at under
        the relevant proof standards, given the beliefs of the audience.
        """
        
        standard = self.standard.assign_standard(proposition)
        logging.debug("Checking whether proposition '{}' meets proof standard '{}'.".format(proposition, standard))
        return self.meets_proof_standard(proposition, standard)
                
  
    def meets_proof_standard(self, proposition, standard):
        arguments = self.argset.arguments_pro_and_con(proposition)
        
        if standard == 'scintilla':
            result = any(arguments)
            logging.debug("Proposition '{}' meets standard '{}': {}".format(proposition, standard, result))
            return result
        
        
    def weight_of(self, argument):
        arg_id = argument.arg_id
        try:
            return self.weight[arg_id]            
        except KeyError:
            raise ValueError("No weight assigned to argument '{}'.".format(arg_id))
        
        
    def max_weight_applicable(self, arguments):
        """
        :parameter arguments: The arguments whose weight is being compared.
        :type arguments: list(:class:`Argument`)
        :return: The maximum of the weights of the arguments.
        :rtype: int
        """
        arg_ids = [arg.arg_id for arg in arguments]
        logging.debug('Checking applicability and weights of {}'.format(arg_ids))
        applicable_args = [arg for arg in arguments if self.applicable(arg)]
        aaplic_arg_ids = [arg.arg_id for arg in applicable_args]
        logging.debug('Checking applicability and weights of {}'.format(aaplic_arg_ids))
        weights = [self.weight_of(argument) for argument in applicable_args]
        logging.debug('Weights of {} are {}'.format(aaplic_arg_ids, weights))
        return max(weights)
        


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
    g.es['arg'] = ['arg1', 'arg2']
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

