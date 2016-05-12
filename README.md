## Random Map Generation

[I. Cellular Automata Method for Generating Random Cave-Like Levels (Implemented)](http://www.jimrandomh.org/misc/caves.html)
```
   # True: WALL   False: FLOOR
   
   # There is a wall initially at P with fill_prob probability
   W[0](p) = rand() < fill_prob
   # R[n](p): number of tiles within n step of p which are walls
   Repeat nrepeats: 
      W'(p) = R[1](p) >= r1_cutoff || R[2](p) <= r2_cutoff 
      
   Connect up disjoint regions
       # basic algorithm. how to optimize it :-)
       select one point in each of two regions randomly, denoted by p1 & p2
       while p1 is not same position as p2:
          select a moving direction randomly from {up, down, left, right} 
          next := next position from p1 in that direction
          if next is not closer to p2 than p1:
              continue
          update p1 to next
```

```
size = 60 x 30  fill_prob = 0.4  r1_cutoff = 5 r2_cutoff = 2 nrepeats = 10

# Wall  . Floor

############################################################
#############..###...........###########.......#############
#####....###..................#########..............#######
####..........................####..##......####........####
###...##.....#........#..##..#####......#.....#######...####
####.####...###......#############.....##...#..######...####
#########....#...##..#############.##.###..###..####..######
########........####..###########..#..###.#####..##..#######
####.....##.....####..###########..#..##########......######
###.....####.....##..############..#..###.######.........###
##.....########.....#####....#####....###..####...##......##
##.....#########...####.......####....###.........###.....##
#..##..###############...####...##............###..####...##
#..###..##############..#####.......##......######..###...##
#..####......########.....##..##...#####...#######..###...##
#...####.........###.........####.....###..######...###...##
##..#####..##...........##...####.###.###..#####...####..###
###..###...##........#..##...###..###...##..###....#########
###............##...###.....####...####.##.........#########
###.......#...####..###....#####..................##########
###..##...##..####..###..######...................##########
##..####...#...##.......####....##...####.........##########
##..####...###.....#....###....####..#####..###....#########
###..###....##.....##...###..#.####...###.....##....########
###.............#..##..####.....##.........##.##.....####.##
####.....####...#.....######................#.#.......##...#
##############.......##########...........................##
##############.....##############..#######.......####....###
###############..###########################################
############################################################
```

[II. Rooms and Mazes: A Procedural Dungeon Generator (Implemented)](http://journal.stuffwithstuff.com/2014/12/21/rooms-and-mazes/)
```
  Rooms and corridors always fall along odd-numbered columns and rows, 
  and rooms are always odd numbers in width and height.
  1. place rooms randomly but not colliding rooms previously placed
  2. generate corridors (randomly)
  3. calculates all possible positions where it may place doors
  4. use a spanning tree algorithm to place doors
  5. removes all dead ends in the matrix, which may make the dungeon 
     more fun to play
  
  POI(path of interest) Finding: 
    POI is a path which should be sufficiently long and a player has 
    a big interest to travel on.
    We use a graph derived from a dungeon to calculate POI. 
    Nodes(Vertices): 
        - rooms
        - doors
        - branching points
        - sets of continuous corridors between doors and branching points 
      Each node has a predefined weight value (aka cost)
    Edges: every pair of nodes that are adjacent are connected in the 
           graph
    Length of a path: he sum of weights of nodes on the path
    POI: a longest path among shortest paths between any pairs of nodes 
         in the graph
```
```
# Solid Rock    + Room    x Door    space Corridor    . POI 

#################################################################################
###########+++###############+++++++###+++++###+++++###+++#######+++++#......####
###########+++###############+++++++###+++++###+++++###+++#######+++++#.####.####
###########+++###########+++#+++++++###+++++###+++++###+++#######+++++x.####..###
###########x########### x+++#+++++++######x####x#######x###############.#####.###
#########+++++######### #+++x+++++++#   #+++#+++++++###....####.....###.####..###
#########+++++######### #####x####### # x+++#+++++++x ..##.####x###..#..####.####
#########+++++#########       ######  ###+++#+++++++##.###.##+++++##...####..####
##########x############## ###x#####  #################.#...##+++++###x####..#####
#+++++####  #######.....#   #+++++# ########...######..#.####+++++#+++++##.######
#+++++#####  ######.###.### #+++++#   ....#..#.######.##.####+++++#+++++#..######
#+++++#+++##   ###..###..   #+++++####.##.#.##........##.####+++++#+++++#.#######
#+++++x+++####...#.#####.##########....##.#.############.################.#######
#+++++#+++####.#...#####..##........#####...###+++#......####          ...#######
##x####+++####.##########.#..###x#########x####+++x.######### #########.#########
#...###+++####.##+++++++#...###+++#####+++++###+++#.#+++++++# #+++++++#..########
#.#..########..##+++++++# #####+++#####+++++#######.#+++++++# #+++++++##.#   ####
#.##.########.###+++++++# #+++#+++#####+++++#+++++#.#+++++++x #+++++++#..# # ####
#..#..#######...#######x# #+++###############+++++#.#+++++++# #+++++++#.## #   ##
##.##..########.#+++++x   #+++############# x+++++#.#+++++++# #+++++++#..# ###  #
#..###...#...#..#+++++# ###+++############  #+++++#.#########x######x###.  #### #
#.######...#...##+++++# ###+++#########    ##+++++#.####...##+++#........###### #
#...#############+++++#   ###x######### # #########.###..#.##+++#.##### ####### #
###...#........##+++++### ### #+++++++# #  ##   ###.....##.##+++#.x+++#   x+++# #
#####...######x##x#####     # #+++++++# ## #  # ##########.##+++###+++#####+++# #
#########+++++++# ####  # #   #+++++++# ##   ## ####      ..#+++###+++x+++#+++# #
#########+++++++# ###  ##x###########x# ##x#### ##   ####x#.#######x###+++#+++# #
#########+++++++# ### ###+++++++#####   #+++++#  # ####+++#.##...##.###+++#+++# #
#########+++++++#   # ###+++++++#########+++++## # ####+++#.##.#.##.  ######### #
#########+++++++###   ###+++++++#########+++++##   ####+++#....#....#           #
#################################################################################
```

[III. Basic BSP Dungeon Generation (Implemented)](http://www.roguebasin.com/index.php?title=Basic_BSP_Dungeon_generation)
```
# Solid Rock    + Room    space Corridor

################################################################################
######################################+++++++++#################################
######################################+++++++++#############++++++++++#++++++++#
######################################+++++++++#############++++++++++#++++++++#
######################++++++++++++####+++++++++#############++++++++++#++++++++#
######################++++++++++++####+++++++++             ++++++++++#++++++++#
######################++++++++++++##########################++++++++++ ++++++++#
######################++++++++++++##################################### ########
########################### ########################################### ########
########################### ########################################### ########
########################### ########++++++++#################++++++++##++++++++#
########################### ########++++++++#################++++++++  ++++++++#
########################### ########++++++++####+++++++++++##++++++++##++++++++#
##########+++++++++###+++++++++++###++++++++####+++++++++++  ++++++++##++++++++#
##########+++++++++###+++++++++++###++++++++####+++++++++++##++++++++##++++++++#
##########+++++++++###+++++++++++###++++++++    +++++++++++#####################
##########+++++++++###+++++++++++###############+++++++++++#####################
##########+++++++++   +++++++++++###################### ########################
################### ################################### ########################
########+++++++++++ ###################++++++++######## ########################
########+++++++++++ ###################++++++++######## ########################
########+++++++++++ #######++++++++####++++++++######## ########################
########+++++++++++ #######++++++++####++++++++######## ########################
########## ######## #######++++++++##### ############## ########################
########## ######## #######++++++++##### ############## ########################
########## ######## ############ ####### #########++++++++++####################
########## ######## ############ ####### #########++++++++++####################
########## ######## ############ ####### #########++++++++++####################
########## ######## ############ #######          ++++++++++####################
########## ######## ############ ####### #########++++++++++####################
########## ######## ############ ####++++++++++###++++++++++####################
########## ######## ############ ####++++++++++####### #########################
##########                 ++++++++##++++++++++####### #########################
####+++++++++++############++++++++##++++++++++#####+++++++++###################
####+++++++++++############++++++++##++++++++++#####+++++++++###################
####+++++++++++############++++++++#################+++++++++###################
####+++++++++++############++++++++#################+++++++++###################
####+++++++++++#####################################+++++++++###################
####+++++++++++                                     +++++++++###################
################################################################################
```

[IV. Dungeon Generation in TinyKeep (Implemented)](https://www.reddit.com/r/gamedev/comments/1dlwc4/procedural_dungeon_generation_algorithm_explained/)
```
The basic ideas:
    1. generate cells of random position, width and height within a
       circle (using Uniform Distribution, Normal Distribution)
    2. separate out overlapping cells using simple separation steering 
       behavior 
    3. let cells whose 
	       width >= min_room_width && height >= min_room_height 
	     become rooms
    4. connect rooms with L-shape hallways. we construct a Delaunay 
       Graph with centers of all rooms, and calculates MST of the 
       graph, add some edges with some prob. to the MST, then connect 
       any two rooms if there is an edge between them
    5. clear cells which do not intersect with any L-shape hallways
       (we can let cells that intersect with the L shapes become 
       corridor tiles)
```

```
    x Room    + Cell    # Corridor

                                      ++++++                                    
                         xxxxxx       ++++++                                    
                         xxxxxx       ++++++                                    
                         xxxxxx       ++++++                                    
                         xxxxxx##+++##++++++##################                  
                         xxxxxx  +++                         #                  
                         xxxxxx  +++                         #                  
                         xxxxxx  +++                         #                  
                            #    +++                         #                  
                            #    +++                         #                  
                        xxxxxxx                              #                  
                        xxxxxxx                              #                  
                        xxxxxxx                              #                  
                        xxxxxxx###############+++++###########                  
                        xxxxxxx               +++++          #                  
                        xxxxxxx               +++++          #                  
                           ##                 +++++          #                  
                           ##                 +++++          #                  
                           ##                                #                  
                           ##                                #                  
                           ##                                #                  
                           ##                                #                  
                           ##                                #                  
                       +++++#                             xxxxxx                
                       +++++#                             xxxxxx                
                       +++++#                             xxxxxx                
                       +++++#  ++++++                     xxxxxx                
               xxxxxx  +++++#  ++++++                     xxxxxx                
               xxxxxx      ##  ++++++                     xxxxxx                
               xxxxxx      ##  ++++++  ++++++                #                  
               xxxxxx##########++++++##++++++#################                  
               xxxxxx       ##       # ++++++                #                  
               xxxxxx       ##       # ++++++                #                  
                  #         ##       #                       #                  
                  #         ##   ++++++                      #                  
                  #         ##   ++++++                      #                  
                  #         ##   ++++++                      #                  
    xxxxxxx       #         ##   ++++++                      #                  
    xxxxxxx       #         ##       #                       #                  
    xxxxxxx       #         ##       #                       #                  
    xxxxxxx       #         ##       #                       #                  
    xxxxxxx####++++++#########       #                       #                  
    xxxxxxx    ++++++        #       #                  +++++++                 
    xxxxxxx    ++++++        #       #                  +++++++                 
    xxxxxxx    ++++++        #       #                  +++++++                 
               ++++++        #       #                  +++++++                 
                             #       #                  +++++++                 
                             #       #                       #                  
                             #       #                       #                  
                             #       #                       #                  
                             #       #                       #                  
                             #       #                       #                  
                             #       #                       #                  
                          xxxxxx  xxxxxx       +++++++       #                  
                          xxxxxx  xxxxxx       +++++++       #                  
                          xxxxxx  xxxxxx       +++++++       #                  
                          xxxxxx##xxxxxx#######+++++++########                  
                          xxxxxx  xxxxxx       +++++++                          
                          xxxxxx  xxxxxx                                        
                          xxxxxx                                                
                                              
```

[V. Procedural Level Generation in The Dungeoning](http://www.gamasutra.com/blogs/NickDonnelly/20150629/247283/Procedural_Level_Generation_in_The_Dungeoning.php)
``` 
The main ideas:
    create a list of room-types with predefined descriptions 
    (e.g. size of a room, number of doors of a room, etc)
    select a room as the root room, start from it and iterate 
    through a process as follows:
      1. select a door at random from the list of available doors.
      2. select a room type at random that has a matching sized 
         door on the opposite side of the room so that the two rooms
         can be connected.
      3. check if the new room can be placed on the map in such a 
         way that the doors connect up and that it does not overlap 
         with any existing placed room, and does not cross the edge
         of the available map area. if the room cannot be placed, 
         select another room type and try again.
      4. remove the original door from the available door list and
         add all the doors from the new room to the list (excluding 
         the doors connecting rooms).
```

[VI. Randomization in Diablo III](http://www.diablowiki.net/Randomization)

```
 Map Tiles:
   A map tile is one section within a map. 
   In Diablo III, tiles are generally represented as 
     rooms in a dungeon or various-shaped masses of land
   Each tile is fixed in size and shape, but can contain other elements 
     (say monstors, treasures, chests, etc.) within them.   
 
 A map consists of inter-connected tiles that form the entire dungeon
 and each tile is placed in a random fashion
 
 In Diablo I and II, the maps were, while randomly generated with much 
   smaller tiles, generally the same size (and usually quite large). 
 In Diablo III, a map that is randomly generated has a much wider range 
   of overall size
```
```
  An Discussion Thread on Random Map Generation in Diablo III
      http://us.battle.net/d3/en/forum/topic/6147286293
 
```

[VII. Galak-Z, Forever: Building Space-Dungeons Organically](http://twvideo01.ubm-us.net/o1/vault/gdc2015/presentations/Aikman_Zach_Galak-Z,%20Forever.pdf)

```
  Hilbert Curves
    See http://www.fundza.com/algorithmic/space_filling/hilbert/basics/index.html
```

```
def _hilbert_curve(x, y, xi, xj, yi, yj, n):
    if n == 0:
        return [(x, y)]
        
    sz = 1 << n
    sz_1 = sz - 1
    
    subsz = sz >> 1
    subsz_1  = subsz - 1

    ret =   _hilbert_curve(x, y,
                           yi, yj, xi, xj, n - 1)             \
          + _hilbert_curve(x + xi * subsz, y + xj * subsz,
                           xi, xj, yi, yj, n - 1)             \
          + _hilbert_curve(x + (xi + yi) * subsz, y + (xj + yj) * subsz,
                           xi, xj, yi, yj, n - 1)             \
          + _hilbert_curve(x + xi * subsz_1 + yi * sz_1, y + xj * subsz_1 + yj * sz_1,
                           -yi, -yj, -xi, -xj, n - 1)

    return ret
```

```
# get list of points on hilbert curve of n-th order
def hilbert_curve(n):
    # we start at (0, 0)
    return _hilbert_curve(0, 0, 1, 0, 0, 1, n)
```

[VIII. A List of Useful Links on Map Generation](http://www.roguebasin.com/index.php?title=Articles#Map)