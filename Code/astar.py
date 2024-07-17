import math
from heap import Heap


def astar(self, position, state, lookahead, h, world, extract_best_state):
    open_list = Heap()

    closed_set = set()
    parent = {}

    done = False

    f = {}
    g = {}
    g[(position, state)] = 0

    f[(position, state)] = h[(position, state)] + g[(position, state)]

    open_list.add_node((f[(position, state)], 0), (position, state))

    parent[(position, state)] = None
    while len(open_list) > 0:

        s, open_list = extract_best_state(self.h_dict, h, open_list)

        if (lookahead == 0) or (s[1] in self.automaton.graph['accept']):
            open_list.add_node((0, 0), s)
            break

        self.exp += 1

        world.set_pos(s[0][0], s[0][1])

        closed_set.add(s)
        lookahead -= 1

        for move in world.pos_move(end=False):
            nstate = self.new_state(s[1], move[1][1])
            nposition = move[1][0]
            ns = (nposition, nstate)

            if ns not in h:
                self.calculate_h(nposition, nstate, h)
            if ns not in g:
                g[ns] = math.inf

            succ_cost = g[s] + 1

            if g[ns] > succ_cost:
                parent[ns] = (s, move[0])
                g[ns] = succ_cost
                f[ns] = g[ns] + h[ns]
                if ns in closed_set:
                    closed_set.remove(ns)

                if self.automata_subgoaling:
                    open_list.add_node((self.delta[ns[1]], f[ns], h[ns]), ns)
                else:
                    open_list.add_node((f[ns], h[ns]), ns)

    if s[1] not in self.automaton.graph['accept'] and\
            (lookahead > 0 or len(world.pos_move()) == 0) and not done:
        # no plan can be found
        return None, None, None, None, h

    min_s = s[:]
    ret_s = s[:]
    ret = [(min_s, None)]

    if parent[min_s] is not None:
        while parent[min_s][0] != (position, state):
            ret.append(parent[min_s])
            min_s = parent[min_s][0]
        ret.append(parent[min_s])

    return ret_s, ret[::-1], open_list.open, closed_set, h
