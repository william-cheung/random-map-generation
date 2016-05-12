#
#  Generate random cave-like structures
#      see http://www.jimrandomh.org/misc/caves.html
#          http://www.roguebasin.com/index.php?       \ [LINE-BREAK]
#              title=Cellular_Automata_Method_for_Generating_Random_Cave-Like_Levels
#
#  William Cheung, 4/1/2016
#


import sys, os


class GenerationRule:
    def __init__(self, r1_cutoff, r2_cutoff, reps):
        self.r1_cutoff = r1_cutoff
        self.r2_cutoff = r2_cutoff
        self.reps = reps


class CavesMap:
    TILE_WALL  = 1
    TILE_FLOOR = 0

    def __init__(self, xsize, ysize, fill_prob, gen_rules):
        self._xsize = xsize
        self._ysize = ysize
        self._fill_prob = fill_prob
        self._gen_rules = gen_rules
        self._grid1 = CavesMap._rand_grid(xsize, ysize, fill_prob)
        self._grid2 = CavesMap._rand_grid(xsize, ysize, 1.0)
        for rule in gen_rules:
            self._update(rule)

    @staticmethod
    def _rand_grid(xsize, ysize, fill_prob):
        from random import random
        grid = [[0] * xsize for y in xrange(ysize)]
        for y in xrange(ysize):
            for x in xrange(xsize):
                if random() < fill_prob:
                    grid[y][x] = CavesMap.TILE_WALL
        for y in xrange(ysize):
            grid[y][0] = grid[y][xsize-1] = CavesMap.TILE_WALL
        for x in xrange(xsize):
            grid[0][x] = grid[ysize-1][x] = CavesMap.TILE_WALL
        return grid

    def _update(self, rule):
        for i in xrange(rule.reps):
            self._update_aux(rule.r1_cutoff, rule.r2_cutoff)

    def _update_aux(self, r1_cutoff, r2_cutoff):
        for y in xrange(1, self._ysize-1):
            for x in xrange(1,  self._xsize-1):
                r1, r2 = 0, 0
                for y_off in xrange(-1, 2):
                    for x_off in xrange(-1, 2):
                        if self._grid1[y+y_off][x+x_off] != CavesMap.TILE_FLOOR:
                            r1 += 1
                for y_oth in xrange(y - 2, y + 3):
                    for x_oth in xrange(x - 2, x + 3):
                        if abs(y - y_oth) == 2 and abs(x - x_oth) == 2:
                            continue
                        if y_oth < 0 or y_oth >= self._ysize or \
                            x_oth < 0 or x_oth >= self._xsize:
                            continue
                        if self._grid1[y_oth][x_oth] != CavesMap.TILE_FLOOR:
                            r2 += 1
                if r1 >= r1_cutoff or r2 <= r2_cutoff:
                    self._grid2[y][x] = CavesMap.TILE_WALL
                else:
                    self._grid2[y][x] = CavesMap.TILE_FLOOR
        for y in xrange(1, self._ysize-1):
            for x in xrange(1,  self._xsize-1):
                self._grid1[y][x] = self._grid2[y][x]

    def get(self, x, y):
        return self._grid1[y][x]

    def set(self, x, y, v):
        self._grid1[y][x] = v

    def get_xsize(self):
        return self._xsize

    def get_ysize(self):
        return self._ysize

    def print_rules(self):
        output = 'W[0](p) = rand() < %f\n' % self._fill_prob
        for rule in self._gen_rules:
            output += 'Repeat %d : W\'(p) = R[1](p) >= %d || R[2](p) <= %d\n' \
                      % (rule.reps, rule.r1_cutoff, rule.r2_cutoff)
        print output

    def __str__(self):
        ret = ''
        for y in xrange(0, self._ysize):
            line = ''
            for x in xrange(0, self._xsize):
                if self._grid1[y][x] == CavesMap.TILE_WALL:
                    line += '#'
                else:
                    line += '.'
            ret += line + '\n'
        return ret


class point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def equals(self, other):
        return self.x == other.x and self.y == other.y


def connect_up_regions(cmap):
    xsize, ysize = cmap.get_xsize(), cmap.get_ysize()
    region_map = [[0] * xsize for i in xrange(ysize)]
    region_cnt = 1
    for y in xrange(ysize):
        for x in xrange(xsize):
            if mark_region(cmap, x, y, region_map, region_cnt):
                region_cnt += 1

    print 'Number of Regions: %d' % (region_cnt - 1)
    regions = [[] for i in xrange(region_cnt)]

    print 'Region Map:'
    output = ''
    for y in xrange(ysize):
        line = ''
        for x in xrange(xsize):
            region_id = region_map[y][x]
            if region_id:
                regions[region_id].append(point(x, y))
            line += '%d' % region_id
        line += '\n'
        output += line
    print output

    max_region_id = get_max_region(regions)
    print 'Max Region : %d' % max_region_id
    for region_id in xrange(1, len(regions)):
        if region_id == max_region_id:
            continue
        print 'connecting %d and %d ...' % (region_id, max_region_id)
        do_connect_regions(cmap, region_map, regions, region_id, max_region_id)


def mark_region(cmap, x, y, region_map, region_id):
    if x < 0 or x >= cmap.get_xsize() or y < 0 or y >= cmap.get_ysize():
        return False
    if cmap.get(x, y) == cmap.TILE_WALL or region_map[y][x] != 0:
        return False
    region_map[y][x] = region_id
    mark_region(cmap, x - 1, y, region_map, region_id)
    mark_region(cmap, x, y - 1, region_map, region_id)
    mark_region(cmap, x + 1, y, region_map, region_id)
    mark_region(cmap, x, y + 1, region_map, region_id)
    return True


def get_max_region(regions):
    ret, max_len = 0, 0
    for i, area in enumerate(regions):
        l = len(area)
        if l > max_len:
            ret, max_len = i, l
    return ret


def do_connect_regions(cmap, region_map, regions, region1_id, region2_id):
    from random import randint
    region1, region2 = regions[region1_id], regions[region2_id]
    pos1 = region1[randint(0, len(region1) - 1)]
    pos2 = region2[randint(0, len(region2) - 1)]

    def __closer(new_pos, old_pos, target):
        def __dist2(p1, p2):
            dx = p2.x - p1.x
            dy = p2.y - p1.y
            return dx * dx + dy * dy
        return __dist2(new_pos, target) < __dist2(old_pos, target)

    xsize, ysize = cmap.get_xsize(), cmap.get_ysize()
    dx, dy = [1, 0, -1, 0], [0, -1, 0, 1]
    while not pos1.equals(pos2):
        dir = randint(0, 3)
        x, y = pos1.x + dx[dir], pos1.y + dy[dir]
        if x < 1 or x >= xsize - 1 or y < 1 or y >= ysize - 1:
            continue
        pos = point(x, y)
        if not __closer(pos, pos1, pos2):
            continue
        if region_map[y][x] == region2_id:
            break
        if cmap.get(x, y) == cmap.TILE_WALL:
            cmap.set(x, y, cmap.TILE_FLOOR)
        pos1 = pos
    return


def print_usage():
    appname = os.path.basename(sys.argv[0])
    print "Usage: %s xsize ysize fill_prob (r1 r2 count)+\n" % appname


def main():
    try:
        xsize, ysize = int(sys.argv[1]), int(sys.argv[2])
        fill_prob = float(sys.argv[3])
        argc = len(sys.argv)
        rules = []
        for i in range(4, argc, 3):
            r1_cutoff = int(sys.argv[i])
            r2_cutoff = int(sys.argv[i+1])
            reps = int(sys.argv[i+2])
            rules.append(GenerationRule(r1_cutoff, r2_cutoff, reps))
    except:
        print_usage()
        return -1

    cmap = CavesMap(xsize, ysize, fill_prob, rules)
    cmap.print_rules()
    print cmap

    # connect up disjoint segments
    connect_up_regions(cmap)
    print cmap

    return 0


if __name__ == '__main__':
    sys.exit(main())
