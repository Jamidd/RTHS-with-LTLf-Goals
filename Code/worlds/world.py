import random


def get_grid_size(room, map):
    with open(f'worlds/room-map/{room}room_00{map}.map', 'r') as file:
        file.readline()
        grid_size = int(file.readline().strip().split(' ')[1])
        grid_size2 = int(file.readline().strip().split(' ')[1])
    return (grid_size+grid_size2)/2


class World:
    def __init__(self, room=16, map=0, number=3, rep=3):

        self.number = number
        self.repetitions = rep
        self.pos = False
        self.grid = False
        self.step_counter = 0
        self.positions = list()
        self.file = f'{room}-{map}-{number}-{rep}'

        with open(f'worlds/room-map/{room}room_00{map}.map', 'r') as file:
            file.readline()
            self.grid_size = int(file.readline().strip().split(' ')[1])
            file.readline(), file.readline()
            self.grid = []
            change_icon = {'.': ' ', '@': '#', 'T': '#'}

            for _ in range(self.grid_size):
                self.grid.append(
                    [
                        change_icon[x] for x in list(file.readline().strip())
                    ][:self.grid_size]
                )

        self.max_steps = 9999999999999999999999999999999999999

        # Grid[i][j]
        # 0-0 | 0-1 | 0-2 ...
        # 1-0 | 1-1 | 1-2 ...
        # 2-0 | 2-1 | 2-2 ...
        # ... ...  ...
        ###

        pos_used = set()

        while len(pos_used) < self.repetitions * self.number:
            x = random.randint(1, self.grid_size-1)
            y = random.randint(1, self.grid_size-1)
            if self.grid[x][y] == ' ':
                pos_used.add((x, y))
        positions = [list(x) for x in pos_used]

        positions = positions[:(len(positions) // self.number)*self.number]

        self.g_positions = [
                positions[i:i+self.number] for i in
                range(0, len(positions), self.number)
            ]
        self.all_g_positions = set(pos_used)

        # create elements
        p = (
                random.randint(1, self.grid_size-1),
                random.randint(1, self.grid_size-1)
            )
        while (p in pos_used) or (self.grid[p[0]][p[1]] != ' '):
            p = (
                    random.randint(1, self.grid_size-1),
                    random.randint(1, self.grid_size-1)
                )
        self.pos = list(p)
        pos_used.add(tuple(self.pos))

        for (i, j) in pos_used:
            p = [i, j]
            if p == self.pos:
                self.grid[i][j] = 'X'
            else:
                for p_list in self.g_positions:
                    if p in p_list:
                        self.grid[i][j] = chr(97 + p_list.index(p))

        self.step_counter = 0
        self.positions = [self.pos[:]]

        vals = {}
        vals = {i: set() for i in range(len(self.g_positions[0]))}
        for npos in self.g_positions:
            for i, p in enumerate(npos):
                vals[i].add(tuple(p))

        self.goal_pos = vals

    def set_pos(self, i, j):
        self.pos = [i, j]

    def get_info(self, pos):
        pos = list(pos)
        for p_list in self.g_positions:
            if pos in p_list:
                break
        return [pos == x for x in p_list]

    def grid_move(self, move):
        # returns 0 if move could not be excecuted
        # returns 1 otherwise

        # remove position token from the grid
        i, j = self.pos
        self.grid[i][j] = ' '
        if tuple(self.pos) in self.all_g_positions:
            for p_list in self.g_positions:
                if self.pos in p_list:
                    break
            let = chr(97+p_list.index(self.pos))
            self.grid[i][j] = let
        did_move = False

        # check if move is valid
        if move == 'u':
            # cant move up
            if i == 0 or self.grid[i-1][j] == "#":
                self.grid[i][j] = 'X'
                return 0
            self.pos[0] -= 1
            did_move = True

        elif move == 'd':
            # cant move down
            if i == self.grid_size-1 or self.grid[i+1][j] == "#":
                self.grid[i][j] = 'X'
                return 0
            self.pos[0] += 1
            did_move = True

        elif move == 'r':
            # cant move right
            if j == self.grid_size-1 or self.grid[i][j+1] == "#":
                self.grid[i][j] = 'X'
                return 0
            self.pos[1] += 1
            did_move = True

        elif move == 'l':
            # cant move left
            if j == 0 or self.grid[i][j-1] == "#":
                self.grid[i][j] = 'X'
                return 0
            self.pos[1] -= 1
            did_move = True

        self.step_counter += 1
        self.positions.append(self.pos[:])

        if did_move:
            # move position token on to the grid
            i, j = self.pos
            self.grid[i][j] = 'X'
            return 1
        else:
            return 0

    def pos_move(self, end=True, new_position=False):
        pos_moves = []

        if self.step_counter > self.max_steps and end:
            return pos_moves

        for move in 'ludr':
            pos = list(new_position) if new_position else self.pos[:]
            i, j = pos
            # check if move is valid
            if move == 'd':
                # cant move down
                if i == self.grid_size-1 or self.grid[i+1][j] == "#":
                    continue
                pos[0] += 1
                r = self.get_info(pos)
                pos_moves.append((move, (tuple(pos), r)))

            elif move == 'l':
                # cant move left
                if j == 0 or self.grid[i][j-1] == "#":
                    continue
                pos[1] -= 1
                r = self.get_info(pos)
                pos_moves.append((move, (tuple(pos), r)))
            elif move == 'r':
                # cant move right
                if j == self.grid_size-1 or self.grid[i][j+1] == "#":
                    continue
                pos[1] += 1
                r = self.get_info(pos)
                pos_moves.append((move, (tuple(pos), r)))

            elif move == 'u':
                # cant move up
                if i == 0 or self.grid[i-1][j] == "#":
                    continue
                pos[0] -= 1
                r = self.get_info(pos)
                pos_moves.append((move, (tuple(pos), r)))

        return pos_moves

    def get_pos(self):
        return tuple(self.pos)
