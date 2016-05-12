#
#  Implementation of the Procedural Generation Algorithm in
#  TinyKeep (http://tinykeep.com/) in Python
#
#  See:
#
#    https://www.reddit.com/r/gamedev/comments/1dlwc4/         \ [LINE-BREAK]
#        procedural_dungeon_generation_algorithm_explained/
#    http://www.gamasutra.com/blogs/AAdonaac/20150903/252889/  \ [LINE-BREAK]
#        Procedural_Dungeon_Generation_Algorithm.php
#
#    for explanations of the algorithm
#
#  Written by William Cheung, 04/20/2016
#

#_________________________________________________________________________
# Primitive predicates for floating point numbers

def is_zero(x):
    return abs(x) < 1e-6

def is_equal(x, y):
    return is_zero(x - y)

#_________________________________________________________________________
# Utility methods for generating random point or numbers

def random_point_in_ellipse(x, y, width, height):
    # generate a random point in a ellipse region
    # see
    #     http://stackoverflow.com/questions/5837572/          \ [LINE-BREAK]
    #       generate-a-random-point-within-a-circle-uniformly
    #   for more info about the algorithm

    from random import random
    import math

    t = 2.0 * math.pi * random()
    u = random() + random()
    r = u if u < 1.0 else 2.0 - u
    return x + int(width * r * math.cos(t) / 2.0), \
           y + int(height * r * math.sin(t) / 2.0)


def random_point_in_circle(x, y, radius):
    # simple! just a wrapper :)
    return random_point_in_ellipse(x, y, 2 * radius, 2 * radius)


def box_muller_method():
    # using Box-Muller method to generate two values from standard
    # normal distribution
    #   see https://en.wikipedia.org/wiki/Normal_distribution
    from random import random
    import math

    def _sub_expr(x):
        return math.sqrt(-2.0 * math.log(x))

    u, v = random(), random()
    return _sub_expr(u) * math.cos(2 * math.pi * v), \
           _sub_expr(u) * math.sin(2 * math.pi * v)


def normal_distribution(mu, sigma):
    # generate a pair of values from normal distribution N(mu, sigma)
    u, v = box_muller_method()
    return int(mu + sigma * u), int(mu + sigma * v)

#_________________________________________________________________________
# A "great" utility class for manipulating points and vectors ( Really ? )

class Vector2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def len_squared(self):
     return self.x * self.x + self.y * self.y

    def len_(self):
        from math import sqrt
        return sqrt(self.len_squared())

    def add_(self, other):
        self.x += other.x
        self.y += other.y

    def sub_(self, other):
        self.x -= other.x
        self.y -= other.y

    def mul_(self, n):
        self.x *= n
        self.y *= n

    def div_(self, n):
        self.x /= n
        self.y /= n

    def normalize(self, length = 1.0):
        self.mul_(1.0 * length / self.len_())

    def is_zero(self):
        return is_zero(self.len_())

    @staticmethod
    def add(v1, v2):
        return Vector2(v1.x + v2.x, v1.y + v2.y)

    @staticmethod
    def sub(v1, v2):
        return Vector2(v1.x - v2.x, v1.y - v2.y)

    @staticmethod
    def dot_product(v1, v2):
        return v1.x * v2.x + v1.y * v2.y

    @staticmethod
    def cross_product(v1, v2):
        return v1.x * v2.y - v2.x * v1.y

    @staticmethod
    def dist(v1, v2):
        v = Vector2.sub(v1, v2)
        return v.len_()

    @staticmethod
    def rand_unit():
        x, y = [1, 0, -1, 0], [0, -1, 0, 1]
        from random import randint
        i = randint(0, 3)
        return Vector2(x[i], y[i])

#_________________________________________________________________________
# Basic algorithms in computational geometry used in our Delaunay
#   Triangulation implementation

# calculate area of a triangle
def triangle_area(A, B, C):
    prod = Vector2.cross_product(Vector2.sub(B, A), Vector2.sub(C, A))
    return abs(prod) / 2.0

# test if a point P is in the triangle region ABC
def point_in_triangle(P, A, B, C):
    s1 = triangle_area(P, A, B)
    s2 = triangle_area(P, B, C)
    s3 = triangle_area(P, C, A)
    s = triangle_area(A, B, C)
    return is_equal(s, s1 + s2 + s3)

# test if a point P is on the line segment AB
def point_on_linesegment(P, A, B):
    d1 = Vector2.dist(P, A)
    d2 = Vector2.dist(P, B)
    d = Vector2.dist(A, B)
    return is_equal(d, d1 + d2)

# calculate /_ABC (in radian)
def angle(A, B, C):
    v1 = Vector2.sub(A, B)
    v2 = Vector2.sub(C, B)
    cos_theta = 1.0 * Vector2.dot_product(v1, v2) / v1.len_() / v2.len_()
    from math import acos
    return acos(cos_theta)

#__________________________________________________________________________
# Delaunay Triangulation
#   see http://www.cnblogs.com/soroman/archive/2007/05/17/750430.html

class Edge:
    def __init__(self, u, v):
        self.u = u
        self.v = v

class Triangle:
    def __init__(self, A, B, C):
        self.A = A
        self.B = B
        self.C = C

    def edges(self):
        return [Edge(self.A, self.B),
                Edge(self.B, self.C),
                Edge(self.C, self.A)]

    def __eq__(self, other):
        s1 = {self.A, self.B, self.C}
        s2 = {other.A, other.B, other.C}
        return s1 == s2

    def __hash__(self):
        return hash(tuple([self.A, self.B, self.C]))

# Delaunay graph constructor
class DelaunayGraph:
    def __init__(self, points):
        self._points = points
        self._npoints = len(points)
        self._triangles = []
        self._compute_triangles()

    def _compute_triangles(self):

        # produce a big auxilliary triangle containing all points
        M = 0
        for point in self._points:
            m = max(point.x, point.y)
            M = max(m, M)
        self._points += [Vector2(3 * M, 0),
                         Vector2(0, 3 * M),
                         Vector2(-3 * M, -3 * M)]
        n = self._npoints
        self._triangles.append(Triangle(n, n + 1, n + 2))
        # Note: we use indices of vertices instead of vectices themselves
        #       to construct triangles

        # use an incremental alorithm whose complexity is O(n^2) to
        # construct a Dulaunay Graph
        for i in xrange(n):
            # iterative flipping (known as the Lawson flip)
            self._incremental_delaunay(i)

        # remove the auxilliary bounding triangle and relative triangles
        # which cotain any vertex of it
        remove_set = []
        for t in self._triangles:
            if t.A >= n or t.B >= n or t.C >= n:
                remove_set.append(t)
        for t in remove_set:
            self._triangles.remove(t)

    def _print_triangles(self):
        for t in self._triangles:
            print t.A, t.B, t.C

    def _incremental_delaunay(self, i):

        def __batch_flip_test(t_list):
            for t_ in t_list:
                if not self._lawson_flip(t_):
                    self._triangles.append(t_)

        # find triangles that contain _point[i]
        t = self._locate_triangle(i)

        # if the point is in only one triangle
        if len(t) == 1:
            self._triangles.remove(t[0])

            batch = [Triangle(t[0].A, t[0].B, i),
                     Triangle(t[0].B, t[0].C, i),
                     Triangle(t[0].C, t[0].A, i)]
            __batch_flip_test(batch)

        # if the point is on the common edge of two triangles
        elif len(t) == 2:
            self._triangles.remove(t[0])
            self._triangles.remove(t[1])

            v = self._merge_triangles(t[0], t[1])

            #       v[0]
            #        /\
            #       /  \
            #  v[1] ----   v[3]
            #       \  /
            #        \/
            #       v[2]
            #
            #   _point[i] is on the edge <v[1], v[3]>

            batch = [Triangle(v[0], v[1], i),
                     Triangle(v[1], v[2], i),
                     Triangle(v[2], v[3], i),
                     Triangle(v[3], v[0], i)]
            __batch_flip_test(batch)

        else:
            raise Exception('wrong len(t), 1 or 2 expected')


    def _locate_triangle(self, point_idx):
        P = self._points[point_idx]
        ret = []
        for t in self._triangles:
            A, B, C = self._triangle_points(t)
            if point_in_triangle(P, A, B, C):
                ret.append(t)
        return ret

    def _triangle_points(self, t):
        return self._points[t.A], self._points[t.B], self._points[t.C]

    # get the four vertices of quad formed by two triangles that share
    # a common edge
    def _merge_triangles(self, t1, t2):
        s1 = {t1.A, t1.B, t1.C}
        s2 = {t2.A, t2.B, t2.C}

        l1 = list(s1.difference(s2))
        l2 = list(s2.difference(s1))
        l3 = list(s1.intersection(s2))

        assert len(l1) == 1
        assert len(l2) == 1
        assert len(l3) == 2

        return l1 + [l3[0]] + l2 + [l3[1]]

    # Lawson Flip
    #   returns True if an edge is flipped, otherwise False
    def _lawson_flip(self, t):
        r, q = self._locate_triangle2(t.A, t.B)
        if r is None:
            return False

        def __p(i):
            return self._points[i]

        from math import pi
        a1 = angle(__p(t.A), __p(q), __p(t.B))
        a2 = angle(__p(t.A), __p(t.C), __p(t.B))
        if a1 + a2 < pi:
            return False

        self._triangles.remove(r)
        self._triangles.append(Triangle(t.A, t.C, q))
        self._triangles.append(Triangle(t.B, t.C, q))
        return True

    # find _THE_ triangle one of whose edges is <p1_idx, p2_idx>
    #  if there is one
    def _locate_triangle2(self, p1_idx, p2_idx):
        r = {p1_idx, p2_idx}
        for t in self._triangles:
            s = {t.A, t.B, t.C}
            if r.issubset(s):
                return t, list(s.difference(r))[0]
        return None, -1

    # construct adjacency list of the graph
    def adjacency_list(self):
        ret = []
        for i in xrange(self._npoints):
            ret.append(set())
        for t in self._triangles:
            ret[t.A].add(t.B)
            ret[t.A].add(t.C)
            ret[t.B].add(t.C)
            ret[t.B].add(t.A)
            ret[t.C].add(t.A)
            ret[t.C].add(t.B)
        return ret

#__________________________________________________________________________
# The Dungeon Generator 

# Generator settings
class Settings:
    def __init__(self, config_file):
        import json
        fp = open(config_file)
        try:
            self._settings = json.load(fp)
        finally:
            fp.close()

    def __getitem__(self, item):
        return self._settings[item]


# Class for representation of cells and rooms in our dungeon generator
class Rect:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.w = width
        self.h = height
        self.v = Vector2(0, 0)

    def location(self):
        return Vector2(self.x, self.y)

    def center(self):
        return Vector2(self.x + self.w / 2, self.y + self.h / 2)

    def overlaps(self, other):
        x1 = max(self.x, other.x)
        x2 = min(self.x + self.w, other.x + other.w)
        y1 = max(self.y, other.y)
        y2 = min(self.y + self.h, other.y + other.h)
        return x1 <= x2 and y1 <= y2

# The generator class
class Dungeon:
    TILE_ROOM = 0x01
    TILE_ROCK = 0x02
    TILE_CORR = 0x04  # corridors
    TILE_CELL = 0x08

    def __init__(self, settings):
        self._width  = settings['dungeon_width']    # width of the dungeon
        self._height = settings['dungeon_height']   # height of the dungeon

        self._ncells_exp = settings['cells_expected']   # number of cells expected
        self._cellsz_exp = settings['cellsz_expected']  # expected cell size (width or height)
        self._cellsz_dev = settings['cellsz_deviation'] # standard deviation of cell size

        # max. no. of attempts to relocate cells
        self._reloc_attempts  = settings['reloc_attempts']

        # min. size of rooms
        self._min_room_width  = settings['min_room_width']
        self._min_room_height = settings['min_room_height']

        # prob. of loops when constructing EMST (Euclidean Minimum Spanning Tree)
        self._cycle_edge_prob = settings['cycle_edge_prob']

        self._cells = None
        self._rooms = None

        # a dungeon is constructed as a two-dimensional matrix
        self._rep_mat = None

    def generate(self):
        print 'Cells Expected: %d' % self._ncells_exp

        self._rep_mat = [[Dungeon.TILE_ROCK] * self._width for i in xrange(self._height)]

        # generate cells of random position, width and height within a circle
        self._make_cells()

        # separate out overlapping cells
        self._relocate_cells()

        print 'Cells Generated: %d' % len(self._cells)

        # cells whose width >= _min_room_width and height >= _min_room_height
        # become rooms
        self._select_rooms()

        print 'Rooms Generated: %d' % len(self._rooms)

        # connect rooms with L-shape hallways
        self._connect_rooms()

        # clear cells which do not intersect with any L-shape hallways
        #  (we can let cells that intersect with the L shapes become corridor tiles)
        self._clear_cells()

        print 'Result Cells: %d' % len(self._cells)

        # mark out cells and rooms in the representation matrix (self._rep_mat)
        self._mark_out_cells()
        self._mark_out_rooms()

    def _make_cells(self):
        # generate cells with random width and random height that are placed
        # randomly inside a circle

        # geometry of the circle
        center_x, center_y = self._width / 2, self._height / 2
        radius = min(self._width, self._height) / 4

        self._cells = []
        for i in xrange(self._ncells_exp):
            x, y = random_point_in_circle(center_x, center_y, radius)

            # use normal distribution to generate width and height of cells
            w, h = normal_distribution(self._cellsz_exp, self._cellsz_dev)

            # adjust position of the cell
            x -= w / 2
            y -= h / 2

            self._cells.append(Rect(x, y, w, h))

    def _relocate_cells(self):
        # use simple separation steering behaviour to separate out all of the
        # cells so that none are overlapping

        # number of attempts to separating out cells
        max_step = self._reloc_attempts

        step = 0

        while True:
            # a active cell is a cell that overlaps another cell
            active_cells = self._get_active_cells()
            if not active_cells:
                break

            self._relocate_step(active_cells)

            step += 1
            if step == max_step:
                # if we have reached the max no. of attempts and still have
                # some cells active, we just clear these cells
                self._clear_active_cells(active_cells)
                break

        # clear cells that are out of dungeon bounds
        self._clear_oob_cells()

    def _get_active_cells(self):
        active_cells = []
        for cell in self._cells:
            is_active = False
            for other in self._cells:
                if other is cell:
                    continue
                if other.overlaps(cell):
                    is_active = True
                    break
            if is_active:
                active_cells.append(cell)
        return active_cells

    def _clear_active_cells(self, active_cells):
        for cell in active_cells:
            self._cells.remove(cell)

    def _clear_oob_cells(self):
        # oob: out of bounds
        remove_set = []
        for cell in self._cells:
            if cell.x < 0 or cell.y < 0 or cell.x + cell.w > self._width or \
                cell.y + cell.h > self._height:
                remove_set.append(cell)
        for cell in remove_set:
            self._cells.remove(cell)

    def _relocate_step(self, active_cells):
        # The idea of the algorithm to space out overlapping rectangles if from:
        #   http://stackoverflow.com/questions/3265986/   \ [LINEBREAK]
        #     an-algorithm-to-space-out-overlapping-rectangles

        coeff_1, coeff_2 = 1.0, 4.0

        for cell in active_cells:
            velocity = Vector2(0, 0)

            for other in active_cells:
                if other is cell:
                    continue

                if not other.overlaps(cell):
                    continue

                diff = Vector2.sub(cell.center(), other.center())
                dist = diff.len_squared()

                if is_zero(dist):
                    dist = 1.0
                    diff = Vector2.rand_unit()

                scale = coeff_1 / dist
                diff.normalize(scale)

                velocity.add_(diff)

            if not velocity.is_zero():
                velocity.normalize(coeff_2)

            cell.x += int(round(velocity.x))
            cell.y += int(round(velocity.y))

    def _select_rooms(self):
        w_thresh, h_thresh = self._min_room_width, self._min_room_height
        self._rooms = []
        for cell in self._cells:
            if cell.w >= w_thresh and cell.h >= h_thresh:
                self._rooms.append(cell)

        for room in self._rooms:
            # "we are rooms, not cells now!"
            self._cells.remove(room)

    def _connect_rooms(self):
        # link rooms together

        # get centers of the rooms
        centers = []
        for room in self._rooms:
            centers.append(room.center())

        # construct a graph of all of the rooms' centers using Delaunay
        # Triangulation (i.e. Delaunay Graph)
        graph = DelaunayGraph(centers)
        adjlist = graph.adjacency_list()

        # calculate MST of the graph
        edges = self._pseudo_EMST(adjlist)
        for edge in edges:
            self._create_hallways(edge.u, edge.v)

    def _pseudo_EMST(self, adjlist):
        n = len(adjlist)
        edges = []

        for u in xrange(n):
            for v in adjlist[u]:
                if u < v:
                    edges.append(Edge(u, v))

        def __weight(edge):
            c1 = self._rooms[edge.u].center()
            c2 = self._rooms[edge.v].center()
            return Vector2.dist(c1, c2)

        edges.sort(cmp=lambda e1, e2: __weight(e1) < __weight(e2))

        return self._aux_pseudo_EMST(edges)

    def _aux_pseudo_EMST(self, edges):
        # caculating MST using Kruskal's algorithm

        n = len(self._rooms)
        cycle_edge_prob = self._cycle_edge_prob

        # Union-Find
        L = []
        for i in xrange(n):
            L.append(i)

        def __find(x):
            if L[x] == x:
                return L[x]
            L[x] = __find(L[x])
            return L[x]

        def __union(x, y):
            L[x] = __find(y)

        # Kruskal's Algorithm
        mst_edges = []
        for edge in edges:
            if __find(edge.u) == __find(edge.v):
                from random import random
                if random() < cycle_edge_prob:
                    mst_edges.append(edge)
            else:
                __union(edge.u, edge.v)
                mst_edges.append(edge)

        return mst_edges

    def _create_hallways(self, room_idx1, room_idx2):
        # conect two room with a L-shape hallway
        room1, room2 = self._rooms[room_idx1], self._rooms[room_idx2]
        cent1, cent2 = room1.center(), room2.center()
        if cent1.x > cent2.x:
            cent1, cent2 = cent2, cent1

        x, y = cent1.x, cent1.y
        while x <= cent2.x:
            self._rep_mat[y][x] = Dungeon.TILE_CORR
            x += 1

        if cent1.y > cent2.y:
            x, y = cent2.x, cent2.y
            while y <= cent1.y:
                self._rep_mat[y][x] = Dungeon.TILE_CORR
                y += 1
        else:
            x, y = cent2.x, cent1.y
            while y <= cent2.y:
                self._rep_mat[y][x] = Dungeon.TILE_CORR
                y += 1

    def _clear_cells(self):
        def __is_wanted(cell):
            # test if a cell intersects with any hallway
            for y in xrange(cell.y, cell.y + cell.h):
                for x in xrange(cell.x, cell.x + cell.w):
                    if self._rep_mat[y][x] == Dungeon.TILE_CORR:
                        return True
            return False

        cells_wanted = []
        for cell_ in self._cells:
            if __is_wanted(cell_):
                cells_wanted.append(cell_)
        self._cells = cells_wanted

    def _mark_out_rooms(self):
        for room in self._rooms:
            for y in xrange(room.y, room.y + room.h):
                for x in xrange(room.x, room.x + room.w):
                    self._rep_mat[y][x] = Dungeon.TILE_ROOM

    def _mark_out_cells(self):
        for cell in self._cells:
            for y in xrange(cell.y, cell.y + cell.h):
                for x in xrange(cell.x, cell.x + cell.w):
                    self._rep_mat[y][x] = Dungeon.TILE_CELL

    def print_(self):
        if not self._rep_mat:
            raise Exception('You _SHOULD_ call generate() first')

        def __symbol(type):
            if type == Dungeon.TILE_ROOM:
                return 'x'
            if type == Dungeon.TILE_CELL:
                return '+'
            if type == Dungeon.TILE_CORR:
                return '#'
            if type == Dungeon.TILE_ROCK:
                return ' '
            raise Exception('Undefined dungeon tile')

        output = ''
        for y in xrange(self._height):
            for x in xrange(self._width):
                output += __symbol(self._rep_mat[y][x])
            output += '\n'

        print output

#__________________________________________________________________________
# Code for Testing

def main():
    settings = Settings('tinykeep-config.json')
    dungeon = Dungeon(settings)
    dungeon.generate()
    dungeon.print_()

if __name__ == '__main__':
    main()


