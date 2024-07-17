from base_ltl_algorithms import LTL_ALGORITHM
from normal_ebs import extract_best_state


class LTL_LRTA(LTL_ALGORITHM):

    def run(
        self,
        heuristic=0,
        automata_subgoaling=False,
        seed=False,
        lookahead=10,
        room=8,
        map=0,
        number=3,
        rep=3,
        world_file=None,
    ):
        self.extract_best_state = extract_best_state
        return self._run(
            heuristic,
            automata_subgoaling,
            seed,
            lookahead,
            room,
            map,
            number,
            rep,
            world_file,
        )
