import math


class Sub:
    def __init__(self, info, w, h0):
        self.info = info
        self.w = w
        self. h0 = h0
        self.next_state = {}
        for state in info.automaton.nodes():
            self.next_state[state] = set()
            for _, nstate, labels in \
                    info.automaton.out_edges(state, data=True):
                for label in labels['label']:
                    for x in w.goal_pos[label.index(True)]:
                        self.next_state[state].add((x, nstate))
        self.final_states = set(self.info.automaton.graph['accept'])

    def calculate(self, pos, state, h):
        return 0, h


class Sub_h(Sub):
    def calculate(self, pos, state, H, oh):
        if state in self.final_states:
            H[(pos, state)] = 0
            oh[(pos, state)] = 0
            return 0
        elif self.info.delta[state] == math.inf:
            H[(pos, state)] = math.inf
            oh[(pos, state)] = math.inf
            return math.inf
        options = self.next_state[state]
        if not options:
            return H[(pos, state)]
        for p, s in options:
            if (p, s) not in oh:
                v = self.calculate(p, s, H, oh)
                H[(p, s)] = v
                oh[(p, s)] = v
        oh[(pos, state)] = min(self.h0(pos, p)+oh[(p, s)] for p, s in options)
        H[(pos, state)] = oh[(pos, state)]
        return H[(pos, state)]


class Sub_hcp(Sub):  # cross product heuristic
    def calculate(self, pos, state, H, oh=dict()):
        options = [
            (p, s) for p, s in self.next_state[state] if
            self.info.delta[s] < math.inf
        ]
        if state in self.info.automaton.graph['accept']:
            oh[(pos, state)] = 0
        elif not options:
            oh[(pos, state)] = math.inf
        else:
            oh[(pos, state)] = min(
                self.h0((pos[0], pos[1]), p) for p, _ in options
            )
        H[(pos, state)] = oh[(pos, state)]


def get_heur_func(info, h, w):
    if h == "h1":
        def h0(s1, s2):
            return 1
    elif h == "hm":  # myopic heuristic
        def h0(s1, s2):
            return abs(s1[0]-s2[0]) + abs(s1[1]-s2[1])
    elif h == "hcp":
        def h0(s1, s2):  # cross product heuristic
            return abs(s1[0]-s2[0]) + abs(s1[1]-s2[1])
        return Sub_hcp(info, w, h0)

    return Sub_h(info, w, h0)
