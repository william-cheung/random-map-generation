
class Maze:
    TILE_ROCK = '#'
    TILE_CORR = ' '

    def __init__(self, width, height, max_corrs):
        assert width % 2 != 0
        assert height % 2 != 0

        self._width = width
        self._height = height

        self._rep = [[Maze.TILE_ROCK] * width for i in xrange(height)]
        self._visited = [[False] * width for i in xrange(height)]
        self._max_corrs = max_corrs
        self._ncorrs = 0
        self._place_corrs(width / 2 + 1, height / 2 + 1)

    def _place_corrs(self, x, y):
        self._rep[y][x] = Maze.TILE_CORR
        self._visited[y][x] = True
        self._ncorrs += 1

        dx, dy = [2, 0, -2, 0], [0, -2, 0, 2]
        dirs = [0, 1, 2, 3]
        from random import shuffle
        shuffle(dirs)
        for d in dirs:
            if self._valid_pos(x + dx[d], y + dy[d]):
                self._rep[y+dy[d]/2][x+ dx[d]/2] = Maze.TILE_CORR
                self._ncorrs += 1
                self._place_corrs(x + dx[d], y + dy[d])

    def _valid_pos(self, x, y):
        if x < 1 or x >= self._width - 1:
            return False
        if y < 1 or y >= self._height - 1:
            return False
        if self._visited[y][x]:
            return False
        if self._ncorrs >= self._max_corrs:
            return False
        return True

    def print_(self):
        output = ''
        for y in xrange(self._height):
            for x in xrange(self._width):
                output += self._rep[y][x]
            output += '\n'
        print output


maze = Maze(41, 41, 400)
maze.print_()
