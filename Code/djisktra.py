import math
from heap import HeapDijks


def djisktra(self, h, openl, closed, w):
    open_list = HeapDijks()
    cont = False
    for node in openl:
        open_list.add_node(h[node], node)
        cont = True
    if not cont:
        return h

    for s in closed:
        h[s] = math.inf

    while len(closed) > 0:
        hs, s = open_list.pop_task()
        if s in closed:
            closed.remove(s)

        # check all states that can be parents of s
        for pos in [x[1][0] for x in w.pos_move(end=False, new_position=s[0])]:

            in_edges = self.in_edges[s[1]]
            for state in in_edges:
                # check if the state is reachable from the new state
                # (pos, state) + action -> (s[0], s[1])
                if self.new_state(state, w.get_info(s[0])) != s[1]:
                    continue

                ns = (pos, state)
                if ns in closed and h[ns] > 1 + hs:
                    h[ns] = 1 + hs
                    open_list.add_node(h[ns], ns)
    return h
