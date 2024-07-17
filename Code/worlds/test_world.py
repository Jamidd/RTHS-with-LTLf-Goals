import random


class World:
    def __init__(self, room="re", map=0, number=3, rep=3):

        # number of elements in the formula
        self.number = number
        # number of each elements in the formula to be placed
        self.repetitions = rep
        self.pos = False
        self.grid = False
        self.step_counter = 0
        self.positions = list()
        self.file = f"{room}-{map}-{self.number}-{self.repetitions}"

        with open(f"worlds/room-map/{room}room_00{map}.map", "r") as file:
            file.readline()
            self.grid_size = int(file.readline().strip().split(" ")[1])
            file.readline(), file.readline()
            self.grid = []
            change_icon = {".": " ", "@": "#", "T": "#"}

            for _ in range(self.grid_size):
                self.grid.append(
                    [change_icon[x] for x in list(file.readline().strip())][
                        : self.grid_size
                    ]
                )

        # max steps to be taken before the game ends
        self.max_steps = 9999999999999999999999999999999999999

        # Grid[i][j]
        # 0-0 | 0-1 | 0-2 ...
        # 1-0 | 1-1 | 1-2 ...
        # 2-0 | 2-1 | 2-2 ...
        # ... ...  ...
        ###
        # Testing rooms
        if room == "re":
            if map == 0:
                self.g_positions = [
                    [[0, 9], [9, 3], [9, 9], [1, 4]],
                ]
            if map == 1:
                self.g_positions = [
                    [[13, 7], [17, 13], [11, 17], [7, 11]],
                ]
            pos_used = set()
            for p_list in self.g_positions:
                for p in p_list:
                    pos_used.add(tuple(p))
            self.all_g_positions = set(pos_used)
            # create elements
            if map == 0:
                self.pos = [4, 0]
            if map == 1:
                self.pos = [24, 24]
            pos_used.add(tuple(self.pos))
            for i, j in pos_used:
                p = [i, j]
                if p == self.pos:
                    self.grid[i][j] = "X"
                else:
                    for p_list in self.g_positions:
                        if p in p_list:
                            self.grid[i][j] = chr(97 + p_list.index(p))

            self.step_counter = 0
            self.positions = [self.pos[:]]

            vals = dict()
            vals = {i: set() for i in range(len(self.g_positions[0]))}
            for npos in self.g_positions:
                for i, p in enumerate(npos):
                    vals[i].add(tuple(p))

            self.goal_pos = vals
            return
        # normal room
        pos_used = set()
        while len(pos_used) < self.repetitions * self.number:
            x, y = random.randint(1, self.grid_size - 1), random.randint(
                1, self.grid_size - 1
            )
            if self.grid[x][y] == " ":
                pos_used.add((x, y))
        positions = [list(x) for x in pos_used]

        positions = positions[: (len(positions) // self.number) * self.number]

        self.g_positions = [
            positions[i: i + self.number]
            for i in range(0, len(positions), self.number)
        ]

        self.all_g_positions = set(pos_used)

        # create elements
        p = (
            random.randint(1, self.grid_size - 1),
            random.randint(1, self.grid_size - 1),
        )
        while (p in pos_used) or (self.grid[p[0]][p[1]] != " "):
            p = (
                random.randint(1, self.grid_size - 1),
                random.randint(1, self.grid_size - 1),
            )
        self.pos = list(p)
        pos_used.add(tuple(self.pos))

        for i, j in pos_used:
            p = [i, j]
            if p == self.pos:
                self.grid[i][j] = "X"
            else:
                for p_list in self.g_positions:
                    if p in p_list:
                        self.grid[i][j] = chr(97 + p_list.index(p))

        self.step_counter = 0
        self.positions = [self.pos[:]]

        vals = dict()
        vals = {i: set() for i in range(len(self.g_positions[0]))}
        for npos in self.g_positions:
            for i, p in enumerate(npos):
                vals[i].add(tuple(p))

        self.goal_pos = vals

    def set_pos(self, i, j):
        self.pos = [i, j]

    def show(self):
        # print grid on the terminal
        img = ""
        for line in self.grid[:-1]:
            line = " | ".join(line)
            img += line + "\n"
            img += "-" * len(line) + "\n"
        img += " | ".join(self.grid[-1]) + "\n"
        print(img)

    def showoc(self, openl, close, pos):
        # print grid on the terminal with showing the positions in the
        #   open and close lists
        openl = set([x[0] for x in openl])
        close = set([x[0] for x in close])
        img = ""
        for i in range(len(self.grid)):
            line = "|"
            for j in range(len(self.grid)):
                if self.grid[i][j] != "#":
                    if (i, j) == pos:
                        line += " X "
                    elif (i, j) in close:
                        line += " C "
                    elif (i, j) in openl:
                        line += " O "
                    else:
                        line += f" {self.grid[i][j]} "
                else:
                    line += "###"
                line += "|"
            line += "\n"
            length = len(line) - 1
            line += "-" * length + "\n"
            img += line
        img = "-" * length + "\n" + img
        print(img)

    def showoch(self, openl, close, pos, h):
        # print grid on the terminal with the heuristic value of the positions
        #    in the open and close lists
        nopenl = {x[0]: h[x] for x in openl}
        nclose = {x[0]: h[x] for x in close}
        img = ""
        for i in range(len(self.grid)):
            line = "|"
            for j in range(len(self.grid)):
                if self.grid[i][j] != "#":
                    if (i, j) == pos:
                        line += "  X  "
                    elif (i, j) in nclose:
                        line += f" {str(nclose[(i,j)]).ljust(3)} "
                    elif (i, j) in nopenl:
                        line += f" {str(nopenl[(i,j)]).ljust(3)} "
                    else:
                        line += f" {self.grid[i][j].ljust(3)} "
                else:
                    line += " ### "
                line += "|"
            line += "\n"
            length = len(line) - 1
            line += "-" * length + "\n"
            img += line
        img = "-" * length + "\n" + img
        print(img)

    def showocs(self, openl, close, state, h):
        # print grid on the terminal with the heuristic value of the positions
        #    in the open and close lists at the defined state
        openl = set([x[0] for x in openl if x[1] == state])
        close = set([x[0] for x in close if x[1] == state])
        img = ""
        for i in range(len(self.grid)):
            line = "|"
            for j in range(len(self.grid)):
                if self.grid[i][j] != "#":
                    if (i, j) in close:
                        line += (
                            f"  {str(h[((i, j), state)]).ljust(3)} "  # '  C  '
                        )
                    elif (i, j) in openl:
                        line += (
                            f"  {str(h[((i, j), state)]).ljust(3)} "  # '  O  '
                        )
                    else:
                        line += f"  {self.grid[i][j].ljust(3)} "
                else:
                    spacer = "###"
                    line += f"  {spacer.ljust(3)} "  # ' ### '
                line += "|"
            line += "\n"
            length = len(line) - 1
            line += "-" * length + "\n"
            img += line
        img = "-" * length + "\n" + img
        print(img)

    def showh(self, state, h):
        # print grid on the terminal with the heuristic value of
        #   each position at the defined state
        print(state)
        img = ""
        for i in range(len(self.grid)):
            line = "|"
            for j in range(len(self.grid)):
                if self.grid[i][j] != "#":
                    if ((i, j), state) in h:
                        if self.grid[i][j] not in {
                            "a",
                            "b",
                            "c",
                            "d",
                            "e",
                            "f",
                            "g",
                            "h",
                            "i",
                            "j",
                            "k",
                            "X",
                        }:
                            line += f"  {str(h[((i, j), state)]).ljust(3)} "
                        else:
                            line += f"  {self.grid[i][j].ljust(3)} "
                    else:
                        line += f"  {self.grid[i][j].ljust(3)} "
                else:
                    line += "  ### "
                line += "|"
            line += "\n"
            length = len(line) - 1
            line += "-" * length + "\n"
            img += line
        img = "-" * length + "\n" + img
        print(img)

    def get_info(self, pos):
        # retuns a list of booleans, where each element indicates if the
        #  position is the goal position of that state
        pos = list(pos)
        for p_list in self.g_positions:
            if pos in p_list:
                break
        return [pos == x for x in p_list]

    def grid_move(self, movement_id):
        # returns 0 if move could not be excecuted
        # returns 1 otherwise

        # remove position token from the grid
        i, j = self.pos
        self.grid[i][j] = " "
        if tuple(self.pos) in self.all_g_positions:
            for p_list in self.g_positions:
                if self.pos in p_list:
                    break
            let = chr(97 + p_list.index(self.pos))
            self.grid[i][j] = let
        move = False

        # check if move is valid
        if movement_id == "u":
            # cant move up
            if i == 0 or self.grid[i - 1][j] == "#":
                self.grid[i][j] = "X"
                return 0
            self.pos[0] -= 1
            move = True

        elif movement_id == "d":
            # cant move down
            if i == self.grid_size - 1 or self.grid[i + 1][j] == "#":
                self.grid[i][j] = "X"
                return 0
            self.pos[0] += 1
            move = True

        elif movement_id == "r":
            # cant move right
            if j == self.grid_size - 1 or self.grid[i][j + 1] == "#":
                self.grid[i][j] = "X"
                return 0
            self.pos[1] += 1
            move = True

        elif movement_id == "l":
            # cant move left
            if j == 0 or self.grid[i][j - 1] == "#":
                self.grid[i][j] = "X"
                return 0
            self.pos[1] -= 1
            move = True

        self.step_counter += 1
        self.positions.append(self.pos[:])

        if move:
            # move position token on to the grid
            i, j = self.pos
            self.grid[i][j] = "X"
            return 1
        else:
            return 0

    def pos_move(self, end=True, new_position=False):
        # end, defines if movement counter should be checked
        # new_position, defines if another position should be used instead
        #   of the current position
        pos_moves = []

        if self.step_counter > self.max_steps and end:
            return pos_moves

        for movement_id in "ludr":
            if not new_position:
                pos = self.pos[:]
            else:
                pos = list(new_position)

            i, j = pos
            # check if move is valid
            if movement_id == "u":
                # cant move up
                if i == 0 or self.grid[i - 1][j] == "#":
                    continue
                pos[0] -= 1
                r = self.get_info(pos)
                pos_moves.append((movement_id, (tuple(pos), r)))

            elif movement_id == "d":
                # cant move down
                if i == self.grid_size - 1 or self.grid[i + 1][j] == "#":
                    continue
                pos[0] += 1
                r = self.get_info(pos)
                pos_moves.append((movement_id, (tuple(pos), r)))

            elif movement_id == "r":
                # cant move right
                if j == self.grid_size - 1 or self.grid[i][j + 1] == "#":
                    continue
                pos[1] += 1
                r = self.get_info(pos)
                pos_moves.append((movement_id, (tuple(pos), r)))

            elif movement_id == "l":
                # cant move left
                if j == 0 or self.grid[i][j - 1] == "#":
                    continue
                pos[1] -= 1
                r = self.get_info(pos)
                pos_moves.append((movement_id, (tuple(pos), r)))
        return pos_moves

    def get_pos(self):
        return tuple(self.pos)


# Sample Usage
# grid = World()
# grid.show()
# print()
# grid.grid_move("d")
# grid.grid_move("r")
# grid.grid_move("r")
# grid.grid_move("d")
# grid.grid_move("d")
# grid.show()
# print(grid.get_info(grid.get_pos()))

# pip install PySimpleAutomata
# pip install ply
