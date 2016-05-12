#
# Binary Space Partitioning Based Dungeon Generation
#   See: http://www.roguebasin.com/index.php?title=Basic_BSP_Dungeon_generation
# 
# Written by William Cheung, 04/18/2016
#  


#__________________________________________________________________________
# Code for debugging

DEBUG = False

def debug_print(message):
    if DEBUG:
        print message

#__________________________________________________________________________
# class Rect

class Rect:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def __str__(self):
        return '(%d, %d, %d, %d)' % (self.x, self.y, self.width, self.height)

#_________________________________________________________________________
# BSP Based Dungeon Generator

class Dungeon:
    TILE_ROOM = 0x01
    TILE_ROCK = 0x02
    TILE_CORR = 0x04  # corridors
    TILE_DOOR = 0x08

    def __init__(self):
        self._width = 80
        self._height = 24
        self._level = 4           # number of levels of target BSP tree
        self._nnodes = 16         # number of nodes of target BSP tree + 1

        self._bsp_tree = None     # stores dungeon spaces generated in the spliting stage
        self._regions = None      # _regions[i]: bounding rect. of rooms in dungeon space _bsp_tree[i]

        self._room_mnw = -1       # min width of rooms
        self._room_mnh = -1       # min height ..
        self._room_mxw = -1       # max width  ..
        self._room_mxh = -1       # max height ..

        self._rep = None          # two-dimensional matrix that represents a generated dungeon


    def set_geometry(self, width, height):
        self._width = width
        self._height = height

    def set_level(self, level):
        assert level > 0
        self._level = level

    def set_roomsz(self, roomsz):
        '''
        :param roomsz: [[min_width, max_width], [min_height, max_height]]
        '''
        mnw, mxw = roomsz[0][0], roomsz[0][1]
        assert mnw > 0 and mnw <= mxw
        mnh, mxh = roomsz[1][0], roomsz[1][1]
        assert mnh > 0 and mnh <= mxh

        self._room_mnw, self._room_mxw = mnw, mxw
        self._room_mnh, self._room_mxh = mnh, mxh

    def generate(self):
        self._rep = [[Dungeon.TILE_ROCK] * self._width for i in xrange(self._height)]

        self._nnodes = 1 << self._level
        self._bsp_tree = [None] * self._nnodes
        self._regions = [None] * self._nnodes

        # split dungeon spaces; number of BSP spliting attempts = _level - 1
        self._update_bsp_tree(1, Rect(1, 1, self._width - 2, self._height - 2))

        # fill leaf nodes of the BSP tree with dungron rooms
        self._place_rooms(1)

        # connecting rooms with corridors in a bottom-up manner
        self._place_corrs()

    def _update_bsp_tree(self, node_idx, rect):
        if rect.width < 3 or rect.height < 3 or node_idx >= self._nnodes:
            return

        self._bsp_tree[node_idx] = rect

        from random import randint
        from random import random

        def __rand(a, b):
            bias = int((b - a) * (1 - 0.618))
            return randint(a + bias, b - bias)

        left_child, right_child = 2 * node_idx, 2 * node_idx + 1
        prob = rect.width * 1.0 / (rect.width + rect.height) # probablity of a vertical split
        if random() < prob:
            split_x = __rand(rect.x + 1, rect.x + rect.width - 2)
            debug_print('node_id = %d  x = %d' % (node_idx, split_x))
            self._update_bsp_tree(left_child,
                                  Rect(rect.x, rect.y, split_x - rect.x, rect.height))
            self._update_bsp_tree(right_child,
                                  Rect(split_x + 1, rect.y, rect.width - split_x - 1 + rect.x, rect.height))

        else:
            split_y = __rand(rect.y + 1, rect.y + rect.height - 2)
            debug_print('node_id = %d  y = %d' % (node_idx, split_y))
            self._update_bsp_tree(left_child,
                                  Rect(rect.x, rect.y, rect.width, split_y - rect.y))
            self._update_bsp_tree(right_child,
                                  Rect(rect.x, split_y + 1, rect.width, rect.height - split_y - 1 + rect.y))

        if left_child < self._nnodes and right_child < self._nnodes and \
                (not self._bsp_tree[left_child] or not self._bsp_tree[right_child]):
            self._bsp_tree[left_child] = None
            self._bsp_tree[right_child] = None

    def _place_rooms(self, node_idx):
        left_child, right_child = 2 * node_idx, 2 * node_idx + 1
        if left_child >= self._nnodes or right_child >= self._nnodes or \
                (not self._bsp_tree[left_child] and not self._bsp_tree[right_child]):
            self._place_room(node_idx)
        else:
            self._place_rooms(left_child)
            self._place_rooms(right_child)

    def _place_room(self, node_idx):
        if self._bsp_tree[node_idx] is None:
            return False

        rect = self._bsp_tree[node_idx]

        if rect.width < self._room_mnw or rect.height < self._room_mnh:
            return False

        from random import randint

        mxw = rect.width if self._room_mxw < 0 else min(rect.width, self._room_mxw)
        mxh = rect.height if self._room_mxh < 0 else min(rect.height, self._room_mxh)

        w = randint(max(3, self._room_mnw), mxw)
        h = randint(max(3, self._room_mnh), mxh)
        x = randint(rect.x, rect.x + rect.width - w)
        y = randint(rect.y, rect.y + rect.height - h)

        '''
        x, y = rect.x, rect.y
        w, h = rect.width, rect.height
        '''

        debug_print("room: %d %d %d %d" % (x, y, w, h))

        # update _regions for leaf nodes
        self._regions[node_idx] = Rect(x, y, w, h)

        for i in xrange(y, y + h):
            for j in xrange(x, x + w):
                self._rep[i][j] = Dungeon.TILE_ROOM

        return True

    def _place_corrs(self):
        for region in self._regions:
            debug_print(str(region))

        for node_idx in xrange(self._nnodes - 1, 1, -2):
            parent, sibling = node_idx / 2, node_idx - 1
            if not self._regions[node_idx] and not self._regions[sibling]:
                continue
            elif self._regions[node_idx] and not self._regions[sibling]:
                self._regions[parent] = self._regions[node_idx]
            elif not self._regions[node_idx] and self._regions[sibling]:
                self._regions[parent] = self._regions[sibling]
            else:
                self._aux_place_corrs(sibling, node_idx)
                self._regions[parent] = self._merge_regions(sibling, node_idx)


    # Note on direction numbers in _aux_place_corrs* :
    #  0 right, 1 up, 2 left, 3 down

    def _aux_place_corrs(self, node_idx1, node_idx2):
        from random import randint
        space1, space2 = self._bsp_tree[node_idx1], self._bsp_tree[node_idx2]
        region1, region2 = self._regions[node_idx1], self._regions[node_idx2]
        if space1.y < space2.y:
            x1, x2 = max(region1.x, region2.x), min(region1.x + region1.width - 1, region2.x + region2.width - 1)
            if x1 <= x2:
                x = randint(x1, x2)
                self._aux_place_corrs_between_points(x, region1.y + region1.height, x, region2.y - 1, 3)
                self._aux_place_corrs_dir(x, region1.y + region1.height - 1, 1)
                self._aux_place_corrs_dir(x, region2.y, 3)
            elif region1.x + region1.width <= region2.x:
                x = randint(region2.x, region2.x + region2.width - 1)
                y = randint(region1.y, region1.y + region1.height - 1)
                self._aux_place_corrs_between_points(region1.x + region1.width, y, x, region2.y - 1, 0)
                self._aux_place_corrs_dir(region1.x + region1.width - 1, y, 2)
                self._aux_place_corrs_dir(x, region2.y, 3)
            else:
                x = randint(region1.x, region1.x + region1.width - 1)
                y = randint(region2.y, region2.y + region2.height - 1)
                self._aux_place_corrs_between_points(x, region1.y + region1.height, region2.x + region2.width, y, 3)
                self._aux_place_corrs_dir(x, region1.y + region1.height - 1, 1)
                self._aux_place_corrs_dir(region2.x + region2.width - 1, y, 2)
        else:
            y1, y2 = max(region1.y, region2.y), min(region1.y + region1.height - 1, region2.y + region2.height - 1)
            if y1 <= y2:
                y = randint(y1, y2)
                self._aux_place_corrs_between_points(region1.x + region1.width, y, region2.x - 1, y, 0)
                self._aux_place_corrs_dir(region1.x + region1.width - 1, y, 2)
                self._aux_place_corrs_dir(region2.x, y, 0)
            elif region1.y + region1.height <= region2.y:
                x = randint(region2.x, region2.x + region2.width - 1)
                y = randint(region1.y, region1.y + region1.height - 1)
                self._aux_place_corrs_between_points(region1.x + region1.width, y, x, region2.y - 1, 0)
                self._aux_place_corrs_dir(region1.x + region1.width - 1, y, 2)
                self._aux_place_corrs_dir(x, region2.y, 3)
            else:
                x = randint(region2.x, region2.x + region2.width - 1)
                y = randint(region1.y, region1.y + region1.height - 1)
                self._aux_place_corrs_between_points(x, region2.y + region2.height, region1.x + region1.width, y, 3)
                self._aux_place_corrs_dir(x, region2.y + region2.height - 1, 1)
                self._aux_place_corrs_dir(region1.x + region1.width - 1, y, 2)

    def _aux_place_corrs_between_points(self, x1, y1, x2, y2, dir):
        if dir == 3: # down
            while y1 < y2:
                self._rep[y1][x1] = Dungeon.TILE_CORR
                y1 += 1
            while x1 >= x2: # left
                self._rep[y1][x1] = Dungeon.TILE_CORR
                x1 -= 1
        elif dir == 0: # right
            while x1 < x2:
                self._rep[y1][x1] = Dungeon.TILE_CORR
                x1 += 1
            while y1 <= y2: # down
                self._rep[y1][x1] = Dungeon.TILE_CORR
                y1 += 1
        else:
            raise Exception('Wrong Arguments')

    def _aux_place_corrs_dir(self, x, y, dir):
        dx, dy = [1, 0, -1, 0], [0, -1, 0, 1]
        while self._rep[y][x] == Dungeon.TILE_ROCK:
            self._rep[y][x] = Dungeon.TILE_CORR
            x += dx[dir]
            y += dy[dir]

    def _merge_regions(self, region_idx1, region_idx2):
        region1, region2 = self._regions[region_idx1], self._regions[region_idx2]
        x1, y1 = min(region1.x, region2.x), min(region1.y, region2.y)
        x2 = max(region1.x + region1.width, region2.x + region2.width)
        y2 = max(region1.y + region1.height, region2.y + region2.height)
        return Rect(x1, y1, x2 - x1, y2 - y1)

    def print_(self):
        if not self._rep:
            raise Exception('You _SHOULD_ call generate() first')

        def __symbol(type):
            if type == Dungeon.TILE_ROOM:
                return '+'
            if type == Dungeon.TILE_CORR:
                return ' '
            if type == Dungeon.TILE_ROCK:
                return '#'
            if type == Dungeon.TILE_DOOR:
                return 'x'
            raise Exception('Undefined dungeon tile')

        output = ''
        for y in xrange(self._height):
            for x in xrange(self._width):
                output += __symbol(self._rep[y][x])
            output += '\n'

        print output

#_________________________________________________________________________
# Code for Testing

def main():
    dungeon = Dungeon()
    dungeon.set_geometry(80, 40)
    dungeon.set_level(6)
    dungeon.set_roomsz([[8, 12], [4, 6]])
    dungeon.generate()
    dungeon.print_()


if __name__ == '__main__':
    main()
