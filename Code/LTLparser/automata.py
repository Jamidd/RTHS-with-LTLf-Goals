import os
import sys

from networkx.algorithms.core import core_number

sys.path.insert(1, './LTLparser/functions')
sys.path.insert(1, './LTLparser/LTLf')

from PySimpleAutomata import automata_IO as AutIO
from Translator import Translator
import networkx as nx
from datetime import datetime

def get_automata(formula, p=False):
    prex = str(abs(hash(datetime.now())))
    # returns graphs and alphabet order
    def send_error(text):
        print(f"ERROR:\n{'-' * len(text)}\n{text}\n{'-' * len(text)}")
        exit()

    translator = Translator()
    #  create required DFAs
    try:
        dfa = [translator.translate(formula, prex, 'dfa.txt', True), ][0]
    except ValueError:
        send_error('There has been a problem, please check your formulas', False)

    # return
    # dfa = get_dfas(dfas, rewards, reward=False, minimize=True)[0]
    if f'{prex}formula.mona' in os.listdir():
        # pass
        os.system(f'rm {prex}formula.mona')
        if p:
            os.system(f'cat {prex}dfa.txt')
        os.system(f'rm {prex}dfa.txt')

    G = nx.DiGraph()
    start = None
    accept = set()
    dfa['initial_state'] = dfa['initial_state'].replace('S0', 'S1')
    for n in dfa['states']:
        n = n.replace('S0', 'S1')
        if n == dfa['initial_state']:
            start = n
        elif n in dfa['accepting_states']:
            accept.add(n)
        G.add_node(n, label=set())

    for i, l in dfa['transitions']:
        if i =='S0':
            continue
        f = dfa['transitions'][(i, l)]
        if i == f:
            G.nodes[i]['label'].add(l)
            continue
        if (i, f) not in G.edges:
            G.add_edges_from([(i, f, {'label': set()})])
        G[i][f]['label'].add(l)
    # G.add_edges_from(trans)

    G.graph['alphabet'] = dfa['alphabet']
    G.graph['start'] = start
    G.graph['accept'] = accept

    # clean automata, keep only edges that make a change with only one True in the edge.
    c = True
    while c:
        c = False
        for e in G.edges(data=True):
            stay = False
            delete = set()
            for l in e[2]['label']:
                if sum([x==True for x in l]) == 1:
                    stay = True
                else:
                    delete.add(l)
            if not stay:
                G.remove_edge(*e[:2])
                c = True
                break
            else:
                for l in delete:
                    G.edges[e[:2]]['label'].remove(l)

    open_list = [start]

    seen = set()
    while len(open_list) >= 1:
        s = open_list.pop(0)
        if s in seen:
            continue
        seen.add(s)
        for _, ns in G.out_edges(s):
            open_list.append(ns)

    eliminar = set(G.nodes()) - seen
    
    # delete unreachable nodes
    G.remove_nodes_from(eliminar)

    return G

# a = get_automata('(~a)Ub')

# print(a)