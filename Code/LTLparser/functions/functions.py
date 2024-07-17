from collections import defaultdict, Counter
import itertools
from PySimpleAutomata import DFA
from copy import  deepcopy
from dd import bdd as _BDD
import re 

def read_logic(file_name):
    f = []
    spacer = '//'
    with open(file_name, "r") as file:
        n = file.readline().strip() + spacer
        while n[:2] == spacer:
            n = file.readline().strip() + spacer

        for _ in range(int(n[:n.index(spacer)])):
            line = file.readline().strip()
            while line[:2] == spacer:
                line = file.readline().strip()
            line += spacer
            f.append(line[:line.index(spacer)])
    return f

def read_pddl(file_name):
    objects = {}
    constraints = ''

    with open(file_name, "r") as file:
        while 1:
            try:
                line = next(file).strip()
            except  StopIteration:
                break
            if ':objects' in line:
                break_flag = False
                while 1:
                    if ')' in line:
                        break_flag = True
                    line = iter(line.replace(')','').split(' '))
                    items = []
                    for item in line:
                        if item != '-':
                            items.append(item)
                        else:
                            name = next(line)
                            objects[name] = items
                    if break_flag:
                        break
                    line = next(file).strip()

            if ':constraints' in line:
                left = 0
                right = 0
                brackets = Counter(line)
                left += brackets['(']
                right += brackets[')']
                while left != right:
                    constraints += line
                    line = next(file).strip()
                    brackets = Counter(line)
                    left += brackets['(']
                    right += brackets[')']
                constraints += f' {line}'
                constraints = constraints.replace(')', ' ) ')
                constraints = constraints.replace('(', ' ( ')
                constraints = re.sub(' +', ' ', constraints)
                constraints = constraints[len(' ( :constraints'):-3].strip()
    return [(objects, constraints)], [1]

def read_formula(file_name, extention):

    if extention == 'ltlf':
        return read_logic(file_name)
    elif extention == 'pltl':
        return read_logic(file_name)
    elif extention == 'pddl3':
        return read_pddl(file_name)
    elif extention == 're':
        return read_logic(file_name)
    
def get_new_state():
    counter = 0
    while 1:
        yield f"""S{counter}"""
        counter += 1


def add_reward(automata, n):
    r = dict()
    for ste in automata['accepting_states']:
        r[ste] = n
    automata['reward'] = r
    return automata


def set_in_out(automata):
    set_in = defaultdict(list)
    set_out = defaultdict(list)
    for ini, lbl in automata["transitions"]:
        end = automata["transitions"][(ini, lbl)]
        if lbl == "": lbl = "TRUE"
        set_in[end].append((ini, lbl))
        set_out[ini].append((end, lbl))
    automata["in"] = set_in
    automata["out"] = set_out
    return automata


def to_expr(bddd, u):
    if u == 1:
        return True
    if u == -1:
        return False
    i, v, w = bddd._succ[abs(u)]
    var = bddd._level_to_var[i]
    p = to_expr(bddd, v)
    q = to_expr(bddd, w)
    if p == False and q == True:
        s = var
    else:
        s = (var, q, p)
    if u < 0:
        s = ('~', s)
    return s


def get_elements(bddd, u):
    if u == 1:
        return [True]
    if u == -1:
        return [False]
    i, v, w = bddd._succ[abs(u)]
    var = bddd._level_to_var[i]
    p = get_elements(bddd, v)
    q = get_elements(bddd, w)
    if p == False and q == True:
        s = [var]
    else:
        s = [var] + q + p
    return s


def get_next(tree, formula, accepted, negative):
    is_neg = {True: '!', False: ""}

    if tree in [True, False]:
        if tree ^ negative == True:  # XOR
            accepted.add(formula)
            return accepted
        elif tree ^ negative == False:
            return accepted

    if type(tree) != tuple:
        return get_next(True, f'{formula}&{is_neg[False]}{tree}', accepted, negative).union(
            get_next(False, f'{formula}&{is_neg[True]}{tree}', accepted, negative))
    else:
        if len(tree) == 2:
            return get_next(tree[1], formula, accepted, not negative)
        return get_next(tree[1], f'{formula}&{is_neg[False]}{tree[0]}', accepted, negative).union(
            get_next(tree[2], f'{formula}&{is_neg[True]}{tree[0]}', accepted, negative))


def bdd_2_all_formulas(tree, negative=False, ):
    is_neg = {True: '!', False: ""}

    if type(tree) != tuple:
        if type(tree) == bool:
            symbol = {True: '', False: '!'}
            return set([f'{is_neg[negative]}{symbol[tree]}'])
        return set([f'{is_neg[negative]}{tree}'])

    elif len(tree) == 2:
        return bdd_2_all_formulas(tree[1], negative=not (negative))

    else:
        if type(tree[1]) == bool:
            if tree[1] ^ negative == True:
                aux = set([f'{is_neg[False]}{tree[0]}'])
                return aux.union(bdd_2_all_formulas(tree[2], negative=negative))

        elif type(tree[2]) == bool:
            if tree[2] ^ negative == True:
                aux = set([f'{is_neg[True]}{tree[0]}'])
                return aux.union(bdd_2_all_formulas(tree[1], negative=negative))

        return get_next(tree[1], f'{tree[0]}', set([]), negative).union(
            get_next(tree[2], f'!{tree[0]}', set([]), negative))

def bdd_to_formula(bddd, bd):
    accepted = bdd_2_all_formulas(to_expr(bddd, bd))
    if type(accepted) != set:
        return str(accepted)
    if len(accepted) > 1:
        return '|'.join(list(accepted))
    else:
        return accepted.pop()

"""
def bdd_to_formula_old(bdd, bd):
    bd = list(bdd.pick_iter(bd))[0]
    simbol = {"True": "", "False": "!"}
    return "&".join([f"{simbol[str(bd[k])]}{k}" for k in bd])#.lower()
"""

def _get_min_formula(bdd, b, depth=0):
    elements = Counter(get_elements(bdd, b))
    del elements[True]
    del elements[False]

    if len(elements) < 2 or depth >= len(bdd.vars):
        return set([bdd_to_formula(bdd, b)])

    maxel = max(elements, key=elements.get)
    maxnum = elements.pop(maxel)
    nextel = max(elements, key=elements.get)
    nextnum = elements.pop(nextel)
    opciones = set([])
    if maxnum - nextnum > 1:
        while bdd.var_at_level(0) != maxel:
            bdd.swap(bdd.vars[maxel], bdd.vars[maxel] - 1, bdd._levels())
            opciones.add(bdd_to_formula(bdd, b))
        return set([min(opciones.union(_get_min_formula(bdd, b, depth + 1)), key=len)])
    else:
        return set([bdd_to_formula(bdd, b)])


def bdd_to_min_formula(bdd, b):
    return _get_min_formula(bdd, b).pop()


def consolidate_paths(automata, eliminate_goal_loop = False):
    transitions = defaultdict(list)
    final_trans = {}
    for trans in automata['transitions']:
        a, lbl = trans
        b = automata['transitions'][trans]

        if lbl == '':
            transitions[(a, b)].append(lbl)
        else:
            if ',' in lbl:
                if not eliminate_goal_loop:
                    final_trans[trans] = b
                elif a != b:
                    final_trans[trans] = b
            else:
                transitions[(a, b)].append(f'({lbl})')

    vocab = list(automata['alphabet'])
    for a, b in transitions:
        bdd = _BDD.BDD()
        bdd.declare(*vocab)
        formula = set(transitions[(a, b)])
        if '' in formula:
            formula.remove('')

        if len(formula) >= 1:
            formula = '|'.join(formula)
            formula2 = bdd_to_min_formula(bdd, bdd.add_expr(formula.upper()))
        else:
            formula2 = ''
        final_trans[(a, formula2)] = b

    automata['transitions'] = final_trans
    return automata

def new_var():
    #TODO improve it 
    var = ['A']
    while 1:
        yield ''.join(var)
        if var[-1] == 'Z':
            var = ['A'] * (len(var) + 1)
        else:
            var[-1] = chr(ord(var[-1])+1)

def dfa_intersection_to_rm(automata, reduce=False, set_reward=True, final_state=False):  # from alberto and https://spot.lrde.epita.fr/ipynb/product.html
    # TODO consolidar caminos equivalentes
    result = {
        'alphabet': set().union(*[x["alphabet"] for x in automata]),
        'states': set(),
        'initial_state': "",
        'accepting_states': set(),
        'transitions': dict(),
        'reward': defaultdict(int)
    }
    sdict = {}
    todo = []
    new_state = get_new_state()

    def dst(state_numbers):
        state_numbers_tuple = tuple(state_numbers)
        p = sdict.get(state_numbers_tuple)
        if p is None:
            p = next(new_state)
            sdict[state_numbers_tuple] = p
            todo.append((state_numbers_tuple, p))
        return p

    result["initial_state"] = dst([aut['initial_state'] for aut in automata])

    #Create new alphabet in case some invalid characters are used
    alpha_dict = {}
    nvar = new_var()

    for a in result['alphabet']:
        alpha_dict[a] = next(nvar)

    bdd = None
    maxima = 0
    while todo:
        tuple_rc, osrc = todo.pop()
        lists_of_transitions = [automata[i]['out'][tuple_rc[i]] for i in range(len(automata))]
        for elements in itertools.product(*lists_of_transitions):
            del bdd
            bdd = _BDD.BDD()
            #bdd.declare(*result["alphabet"])
            bdd.declare(*alpha_dict.values())

            cond = bdd.add_expr("TRUE")
            for ste, edge_cond in elements:
                edge_cond = edge_cond.upper()
                edge_cond = ''.join([alpha_dict[x] if x in alpha_dict else x for x in re.split('(TRUE|FALSE|!|&|\(|\)|\|)', edge_cond)])
                ec = bdd.add_expr(edge_cond)
                cond = bdd.apply('&', cond, ec)

            if bdd.to_expr(cond) != "FALSE":
                reward = sum([automata[i]["reward"][elements[i][0]] for i in range(len(elements)) if elements[i][0] in automata[i]['reward']])
                dest = dst([e[0] for e in elements])
                # TODO: check rm reduce if we want full reduce or to every subgoal
                #if reward > 0:
                #    result["accepting_states"].add(dest)
                if reward > maxima:
                    result["accepting_states"] = set([dest])
                    maxima = reward
                elif reward == maxima:
                    result["accepting_states"].add(dest)

                result["states"].add(osrc)
                result["states"].add(dest)
                # result["reward"][dest] = reward  // This is if you want the reward at the node instead of the edge
                if not set_reward:
                    reward = 0
                result["transitions"][(osrc, bdd_to_formula(bdd, cond))] = (dest, reward) # dest // This is if you want the reward at the node instead of the edge

    if reduce:
        full_transitions = deepcopy(result['transitions'])
        for k in result['transitions']:

            result['transitions'][k] = result['transitions'][k][0]
            """
            if k[0] not in result['accepting_states']:
                result['transitions'][k] = result['transitions'][k][0] # only the next state
            elif result['transitions'][k][0] != k[0]:
                result['transitions'][k] = result['transitions'][k][0] # only the next state
            """
        result = DFA.dfa_co_reachable(result)
        for k in result['transitions']:
            result['transitions'][k] = full_transitions[k]  # return the state and reward
    # rename with actual reward

    rm = {
        'alphabet': set(),
        'states': set(),
        'initial_state': "",
        'accepting_states': set(),
        'transitions': dict(),
    }

    rm["alphabet"] = alpha_dict.values() #result["alphabet"]
    new_states = dict()

    for k in result["states"]: # result["reward"]: // This is if you want the reward at the node instead of the edge
        new_states[k] = f'''{k}''' #  \n{"{"}{result["reward"][k]}{"}"}'''
        rm["states"].add(new_states[k])

    if result["initial_state"] not in new_states:
        new_states[result["initial_state"]] = f"""{result["initial_state"]}\n{"{"}0{"}"}"""

    rm["initial_state"] = new_states[result["initial_state"]]

    if final_state:
        rm['accepting_states'] = result['accepting_states'] 

    beta_dict = {}
    for v, k in alpha_dict.items():
        beta_dict[k] = v

    new_transitions = dict()
    for ini in result["transitions"]:
        if final_state and new_states[ini[0]] in result['accepting_states']:
            continue
        end, reward = result["transitions"][ini]
        transition = ini[1]
        if transition == "":
            transition = "True"
        #ini = (new_states[ini[0]], ini[1]) // This is if you want the reward at the node instead of the edge
        ini = (new_states[ini[0]], str((transition, reward) if reward > 0 else transition))
        end = new_states[end]
        reward = result["reward"][end]
        new_transitions[ini] = end

    rm["transitions"] = new_transitions
    # ''.join([beta_dict[x] for x in re.split('\W', ini[1])])
    rm = consolidate_paths(rm)
    rm["alphabet"] = result["alphabet"]
    transitions = {}
    for s, k in rm['transitions']:
        r = rm['transitions'][(s, k)]
        if len(k) == 0:
            k = k
        elif k[0]+k[-1] == '()':
            t, v = eval(k)
            if len(t) > 0:
                t = ''.join([f'{beta_dict[x]}' if x in beta_dict else x for x in re.split('(TRUE|FALSE|!|&|\(|\)|\|)', t)])
            k = (t, v)
        else:
            k = ''.join([f'{beta_dict[x]}' if x in beta_dict else x for x in re.split('(TRUE|FALSE|!|&|\(|\)|\|)', k)])
        transitions[(s, str(k))] = r
    rm['transitions'] = transitions
    return rm

def get_dfas(automata, rewards, reward=False, minimize=False):


    automata = [set_in_out(aut) for aut in automata]

    automata = [consolidate_paths(aut) for aut in automata]

    if minimize:
        automata = [DFA.dfa_co_reachable(aut) for aut in automata]
    return automata

def automatas_to_rm(automata, rewards, minimize=False, reward = True):
    automatas = get_dfas(automata, rewards, reward=True, minimize = False)
    return dfa_intersection_to_rm(automatas, minimize, reward)

def add_a(formula):
    reserved = set(['&', '|', '~', '!', '-', '<', '>'])
    cont = False
    ret = ''
    for l in formula:
        if l in reserved:
            cont = False
        elif not cont:
            ret += '@'
            cont = True
        ret += l
    return ret

def replace(formula, cambio):
    ret = ''
    for l in re.split('(TRUE|FALSE|!|&|\(|\)|\|)', formula):
        if l in cambio:
            ret += str(cambio[l])
        # elif l not in ['(',')']:
        #     ret += l
        else:
            ret += l
    return ret

def write_hoa(dfa, name):
    transByState = defaultdict(list)
    for trans in dfa['transitions']:
        transByState[trans[0]].append((trans[1], dfa['transitions'][trans]))
    hoa = ''
    hoa += 'HOA: v1\n'
    #hoa += 'name: '
    hoa += f'States: {len(dfa["states"])}\n'
    hoa += f'Start: {dfa["initial_state"].replace("S", "")}\n'
    cambio = {}
    final = []
    for i, val in enumerate(dfa['alphabet']):
        cambio[val] = i
        final.append(val)
    hoa += f'''AP: {len(dfa["alphabet"])} "{'" "'.join(final)}"\n'''
    # for i, leter in  enumerate(dfa["alphabet"]):
    #     hoa += f'Alias: @{leter} {i}\n'
    if len(dfa['accepting_states']) == 0:
        hoa += f'Acceptance: 0 t\n'
    else:
        hoa += f'Acceptance: 1 Inf(0)\n'
    hoa += 'acc-name: buchi\n'
    hoa += 'tool: "FL-AT"\n'
    hoa += 'properties: trans-labels explicit-labels trans-acc deterministic state-acc \n'
    hoa += '--BODY--\n'
    for state in transByState:
        if state in dfa['accepting_states']:
            hoa += f'State: {state.replace("S", "")} {"{"}0{"}"}\n'
        else:
            hoa += f'State: {state.replace("S", "")}\n'
        for lbl, nextS in transByState[state]:
            reward = False
            try:
                lbl, reward = eval(lbl)
            except (SyntaxError, NameError):
                reward = False
            if lbl == '':
                hoa += '[t] '
            else:
                hoa += f'[{replace(lbl, cambio)}] '
            hoa += f'{nextS.replace("S", "")}'
            #TODO: check how to add reward
            # if reward:
            #     hoa += f' {"{"}{reward}{"}"}'
            hoa += '\n'
        hoa += '\n'
    hoa += '--END--\n'

    with open(f'{name}.hoa', 'w') as file:
        file.write(hoa)

def write_rmf(dfa, name, accept):
    rmf = ''
    rmf += f'{dfa["initial_state"]}  # initial state\n'
    if accept:
        rmf += f"[{', '.join([x.replace('S', '') for x in dfa['accepting_states']])}]  # terminal state\n"
    for tra in dfa['transitions']:
        ini = int(tra[0].replace('S', ''))
        end = int(dfa['transitions'][tra].replace('S', ''))
        try:
            lbl, reward = eval(tra[1])
        except (SyntaxError, NameError):
            lbl = tra[1]
            reward = 0
        lbl = lbl if lbl != '' else 'True'
        rmf += f'''({ini}, {end}, '{lbl}', ConstantRewardFunction({reward}))\n'''

    with open(f'{name}.txt', 'w') as file:
        file.write(rmf)

def write_output(output_type, dfa, name):
    if output_type == 'hoa':
        write_hoa(dfa, name)
    elif output_type == 'rmf':
        write_rmf(dfa, name, False)
    elif output_type == 'rmf2':
        write_rmf(dfa, name, True)
