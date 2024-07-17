import sys
from ltllrta import LTL_LRTA
from compare_setup import (
    compare,
    options,
    lookaheads,
    f1,
    f2,
    f3,
    f4,
    f5,
    f6,
    n1,
    n2,
    n3,
    n4,
    n5,
    n6,
)

sys.path.insert(1, "./worlds")

x = int(sys.argv[1])

room, n = options[x]
if n == 1:
    name = "LTL-LRTA*"
    automata_subgoaling = False
elif n == 2:
    name = "LTL-LRTA*A"
    automata_subgoaling = True
else:
    raise ValueError

print(n, room)

filename = f"{name}.csv"

problem_counter = {}

for rep in [3, 25, 100][::-1]:
    for k in lookaheads:
        for heur in [
            "hcp",
            "hm",
            "h1",
        ]:
            for fnum, (formula, number) in enumerate(
                [(f1, n1), (f2, n2), (f3, n3), (f4, n4), (f5, n5), (f6, n6)]
            ):
                compare(
                    rep,  # number of elements of each type
                    k,  # lookahead
                    fnum,  # formula number
                    formula,  # formula
                    number,  # number of elements in the formula
                    heur,  # heuristic type
                    automata_subgoaling,  # automata subgoaling
                    filename,  # file name ending
                    name,  # name of the algorithm
                    room,  # room name
                    LTL_LRTA,  # algorithm class
                    problem_counter,  # problem counter
                )
