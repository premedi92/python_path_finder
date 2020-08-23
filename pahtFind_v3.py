import pygame
import math
import operator
from queue import PriorityQueue

#   V1: working algo and interface. Algo not in main while, disables UI
#   V2: working algo and interface. Algo in main while, can pause algo.
#   V3: able to add barriers while paused, but only on white spaces. Added clear function


WIDTH = 600
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("A* Path Finder Visualization Tool")

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = tuple(map(operator.add, GREEN, RED))
WHITE = tuple(map(operator.add, BLUE, YELLOW))
BLACK = (0, 0, 0)
PURPLE = tuple(map(operator.add, BLUE, RED))
ORANGE = (255, 165, 0)
GREY = (128, 128, 128)
TEAL = (64, 224, 208)


class Spot:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.width = width
        self.x = row * width
        self.y = col * width
        self.color = WHITE  # starts with all white cubes
        self.neighbors = []
        self.total_rows = total_rows

    def get_pos(self):
        return self.row, self.col

    def is_closed(self):  # have we looked at this spot already?
        return self.color == RED

    def is_open(self):
        return self.color == GREEN

    def is_barrier(self):
        return self.color == BLACK

    def is_start(self):
        return self.color == ORANGE

    def is_end(self):
        return self.color == TEAL

    def is_path(self):
        return self.color == PURPLE

    def is_unchecked(self):
        return self.color == WHITE

    def are_neighbors_unchecked(self):
        for neighbor in self.neighbors:
            if neighbor.is_closed() or neighbor.is_open() or neighbor.is_start():
                return False
        return True

    def reset(self):
        self.color = WHITE

    def make_closed(self):
        self.color = RED

    def make_open(self):
        self.color = GREEN

    def make_barrier(self):
        self.color = BLACK

    def make_start(self):
        self.color = ORANGE

    def make_end(self):
        self.color = TEAL

    def make_path(self):
        self.color = PURPLE

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid):
        self.neighbors = []

        # check down
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row + 1][self.col])

        # check up
        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row - 1][self.col])

        # check right
        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col + 1])

        # check left
        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier() :
            self.neighbors.append(grid[self.row][self.col - 1])

    def __lt__(self, other):
        return False


def h(p1, p2):
    x1, y1 = p1  # i am expecting coordinates
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)


def algorithm(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    g_score = {spot: float("inf") for row in grid for spot in row}
    g_score[start] = 0
    f_score = {spot: float("inf") for row in grid for spot in row}
    f_score[start] = h(start.get_pos(), end.get_pos())

    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:  # algo finished
            reconstruct_path(draw, came_from, start, end)
            return True

        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1     # no weighted edges

            if temp_g_score < g_score[neighbor]:    # update the value due to more efficient path
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()

        draw()

        if current != start:
            current.make_closed()

    return False


def reconstruct_path(draw, came_from, start, end):
    current = came_from[end]

    while current != start:
        current.make_path()
        current = came_from[current]
        draw()

    end.make_end()


def make_grid(rows, width):
    grid = []
    gap = width // rows

    for i in range(rows):
        grid.append([])
        for j in range(rows):
            spot = Spot(i, j, gap, rows)
            grid[i].append(spot)

    return grid


def draw_grid(win, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
        for j in range(rows):
            pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))


def draw(win, grid, rows, width):
    win.fill(WHITE)

    for row in grid:
        for spot in row:
            spot.draw(win)

    draw_grid(win, rows, width)
    pygame.display.update()


def get_click_position(pos, rows, width):
    gap = width // rows
    y, x = pos

    row = y // gap
    col = x // gap

    return row, col


def main(win, width):
    rows = 25
    grid = make_grid(rows, width)
    start = None
    end = None

    run = True
    started = False
    paused = False

    while run:
        draw(win, grid, rows, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            elif pygame.mouse.get_pressed()[0]:  # left mouse click
                pos = pygame.mouse.get_pos()
                row, col = get_click_position(pos, rows, width)
                spot = grid[row][col]

                if not started:
                    if not start and spot != end:
                        start = spot
                        start.make_start()

                    elif not end and spot != start:
                        end = spot
                        end.make_end()

                    elif spot != start and spot != end:
                        spot.make_barrier()
                elif paused and spot.is_unchecked():
                    spot.make_barrier()
                    for neighbor in spot.neighbors:
                        neighbor.update_neighbors(grid)

            elif pygame.mouse.get_pressed()[2]:  # right mouse click
                pos = pygame.mouse.get_pos()
                row, col = get_click_position(pos, rows, width)
                spot = grid[row][col]

                if not started:
                    if spot.is_start():
                        start = None
                    elif spot.is_end():
                        end = None
                    spot.reset()

                elif paused and spot.are_neighbors_unchecked():
                    spot.reset()
                    for neighbor in spot.neighbors:
                        neighbor.update_neighbors(grid)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not started and start and end:
                    started = True
                    for row in grid:
                        for spot in row:
                            spot.update_neighbors(grid)

                    # init algo
                    count = 0
                    open_set = PriorityQueue()
                    open_set.put((0, count, start))
                    came_from = {}
                    g_score = {spot: float("inf") for row in grid for spot in row}
                    g_score[start] = 0
                    f_score = {spot: float("inf") for row in grid for spot in row}
                    f_score[start] = h(start.get_pos(), end.get_pos())

                    open_set_hash = {start}

                elif event.key == pygame.K_SPACE and started and not paused:
                    paused = True

                elif event.key == pygame.K_SPACE and started and paused:
                    paused = False

                elif event.key == pygame.K_c and (paused or not started):
                    grid = make_grid(rows, width)
                    start = None
                    end = None
                    started = False
                    paused = False

        # algorithm
        if started and not paused:
            current = open_set.get()[2]
            open_set_hash.remove(current)

            if current == end:  # algo finished
                reconstruct_path(lambda: draw(win, grid, rows, width), came_from, start, end)
                started = False
                continue

            for neighbor in current.neighbors:
                temp_g_score = g_score[current] + 1  # no weighted edges

                if temp_g_score < g_score[neighbor]:  # update the value due to more efficient path
                    came_from[neighbor] = current
                    g_score[neighbor] = temp_g_score
                    f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())
                    if neighbor not in open_set_hash:
                        count += 1
                        open_set.put((f_score[neighbor], count, neighbor))
                        open_set_hash.add(neighbor)
                        neighbor.make_open()

            if current != start:
                current.make_closed()

    pygame.quit()


main(WIN, WIDTH)
