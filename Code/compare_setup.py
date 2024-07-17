from datetime import datetime as dt
import os

from worlds.world import get_grid_size

print("starting new")

options = [
    ("starcraft", 1),
    ("starcraft", 2),
    ("maze32", 1),
    ("maze32", 2),
    ("8", 1),
    ("8", 2),
    ("32", 1),
    ("32", 2),
    ("maze8", 1),
    ("maze8", 2),
]

lookaheads = [32, 64, 128, 256, 512, 1024][::-1]

f1 = "F(a & F(b & F(c & F(d & XF(a)))))"
n1 = 4
f2 = "F(a & F(b & F(c & F(d & F(e & F(f & F(g & F(h & F(i & XF(a))))))))))"
n2 = 9
f3 = "((~b)U(a & XF (b))) & ((~c)U(b & XF (c)))"
n3 = 3
f4 = "F(a & XF (b & XF(c|(d & XF e))))"
n4 = 5
f5 = "G(~d) & ((~(b|c)) U a) & ((~c) U b) & F(a & XF(b & XF(c)))"
n5 = 4
f6 = "F(a)"
n6 = 1

number_maps = 10
random_seed = [853980, 128210, 423420, 273630, 762770]


def compare(
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
    ALGORITHM,  # algorithm class
    problem_counter,  # problem counter
):
    print(f"{formula}, room {room}, h {heur}, {name}")
    csv_filename = f"Results/G{room} - {heur} - rep{rep} - f{formula} - {filename}"  # noqa
    maps_filename = (
        f"Maps/G{room} - h{heur} - rep{rep} - f{formula} - "  # noqa
    )

    if csv_filename not in problem_counter:
        problem_counter[csv_filename] = 0

    seen = 0
    if os.path.exists(csv_filename):
        with open(csv_filename, "r") as file:
            seen = sum(len(line) > 1 for line in file)

    print("counted:", seen)

    for i in range(number_maps):
        grid_size = get_grid_size(room, i)
        print()
        initial_time = dt.now()
        f = 0
        print(csv_filename)
        for nn, seed in enumerate(random_seed):
            print(
                f"Checking - size={grid_size} - look={k} - room={room}"
                + f" - map={i} - h={heur} - fnum={fnum} - #{nn+1}"
                + f" - {(dt.now() - initial_time).seconds//60}:"
                + f"{(dt.now() - initial_time).seconds%60}"
                + " " * 45,
            )

            problem_counter[csv_filename] += 1

            if problem_counter[csv_filename] < seen:
                continue

            search = ALGORITHM(formula)
            t = search.run(
                heuristic=heur,
                automata_subgoaling=automata_subgoaling,
                seed=seed,
                lookahead=k,
                room=room,
                map=i,
                number=number,
                rep=rep,
                world_file=maps_filename,
            )
            if not os.path.exists(csv_filename):
                print("new file")
                with open(csv_filename, "w") as file:
                    file.write(
                        "Algorithm, Lookahead, Room, Map, Grid, Steps, "
                        + "Episodes, Expansions, Time\n"
                    )

            with open(csv_filename, "a") as file:
                file.write(
                    ", ".join(
                        [
                            str(x)
                            for x in [
                                name,
                                k,
                                room,
                                i,
                                grid_size,
                                t[0],
                                t[1],
                                t[2],
                                t[3],
                            ]
                        ]
                    )
                )
                file.write("\n")

            f += t[0]
        print(
            f"Done {grid_size} - look={k} - room={room}{rep}"
            + f" - map={i} - check={nn+1} - time="
            + f"{(dt.now() - initial_time).seconds//60}:"
            + f"{(dt.now() - initial_time).seconds%60} - total={f}"
            + " " * 45,
        )
        print()
