from collections import defaultdict
import os
from time import perf_counter
import math
import random
import pickle
import networkx as netx

from worlds.world import World
from astar import astar
from LTLparser.automata import get_automata
from djisktra import djisktra
from heuristic import get_heur_func


class LTL_ALGORITHM:
    def __init__(self, formula):
        try:
            with open(f'automatas/{formula}.pickle', 'rb') as file:
                self.automaton = pickle.load(file)
        except Exception:
            self.automaton = get_automata(formula)
            with open(f'automatas/{formula}.pickle', 'wb') as file:
                pickle.dump(self.automaton, file)

        self.formula = formula
        self.seed = random.randint(10, 10000)
        # save the path length between all pairs of nodes in the automata
        self.delta = dict(netx.all_pairs_dijkstra_path_length(self.automaton))
        self.delta = {
            x: min(
                    [
                     self.delta[x][y] for y in self.automaton.graph['accept']
                     if (x in self.delta) and (y in self.delta[x])
                    ]+[math.inf, ]
                )
            for x in set(self.automaton.nodes())
        }
        # create a list of the automata states
        self.state_list = list(self.automaton.nodes())
        # dict to save all the states that reach each one
        self.in_edges = {
            state: (
                list({x[0] for x in self.automaton.in_edges(state)}) + [state]
            )
            for state in self.state_list
        }

    def calculate_h(self, pos, state, h):
        self.heur_class.calculate(pos, state, h, oh=self.h_dict)

    def new_state(self, current_state, new):
        # checks that if given an automata state and a position on the grid,
        # we move to a new automata state.
        if True not in new:
            return current_state

        i = new.index(True)
        if (current_state, i) in self.new_state_dict:
            return self.new_state_dict[(current_state, i)]

        for edge in self.automaton.out_edges([current_state]):
            for states in self.automaton[edge[0]][edge[1]]['label']:
                transition = not any(
                    p is not None and p != q for p, q in zip(states, new)
                )
                if transition:
                    self.new_state_dict[(current_state, i)] = edge[1]
                    return edge[1]
        self.new_state_dict[(current_state, i)] = current_state
        return current_state

    def search(self, current_pos, nstate, lookahead, h, w):
        return astar(
            self, current_pos, nstate, lookahead, h, w, self.extract_best_state
        )

    def grid_size(self, room, map, number, rep):
        self.w = World(
            room=room, map=map, number=number,
            rep=rep, automata=len(self.state_list)
        )

    def _run(
        self, heuristic, automata_subgoaling, seed,
        lookahead, room, map, number,
        rep, world_file
    ):
        self.h_dict = {}
        self.automata_subgoaling = automata_subgoaling
        self.current_state = None

        self.contador = defaultdict(int)

        self.heuristic = heuristic
        steps = 0
        # number of search cycles
        self.se = 0
        # number of nodes expanded
        self.exp = 0

        self.current_state = self.automaton.graph['start']
        self.new_state_dict = {}
        self.seed = seed
        world_file += f" - {map} - {self.seed}.pk"
        if not os.path.exists(world_file):
            # create a world
            random.seed(self.seed)
            w = World(
                room=room, map=map, number=number,
                rep=rep
            )
            with open(world_file, "wb") as file:
                pickle.dump(w, file)
        else:
            with open(world_file, "rb") as file:
                w = pickle.load(file)
        # heuristic
        h = {}

        # position on the grid
        current_pos = w.get_pos()

        self.heur_class = get_heur_func(self, self.heuristic, w)

        initial_time = perf_counter()
        self.calculate_h(current_pos, self.current_state, h)
        while self.current_state not in self.automaton.graph['accept']:

            self.se += 1
            state = self.current_state
            # get the search space
            s, fpath, openl, closed, h = self.search(
                current_pos, state, lookahead, h, w
            )

            w.set_pos(current_pos[0], current_pos[1])
            # there are no more steps and we have not found the final goal
            if s is None:
                t = (perf_counter() - initial_time)
                return w.max_steps, self.se, self.exp, t, h

            h = djisktra(self, h, openl, closed, w)
            while (
                self.current_state not in self.automaton.graph['accept']
            ):
                pos, action = fpath.pop(0)  # position, action
                if pos[0] != (current_pos):
                    raise ValueError

                if action is None:
                    break

                if w.grid_move(action):
                    current_pos = w.get_pos()
                    steps += 1
                else:
                    print(
                        'error, move not possible', current_pos, state, action
                    )
                    exit()

                self.current_state = fpath[0][0][1]
                self.contador[(current_pos, self.current_state)] += 1

            if (current_pos, self.current_state) not in h:
                self.calculate_h(current_pos, self.current_state, h)
        t = (perf_counter() - initial_time)
        return steps, self.se, self.exp, t, h
