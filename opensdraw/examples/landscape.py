#!/usr/bin/env python
#
# Landscape file generation for parts-file example. This
# generates a parts text file, then landscape.lcad generates
# the final .mpd file.
#
# Hazen 05/15
#

import math
import numpy
import random

numpy.set_printoptions(precision = 4)

# Generate a landscape using a diamond-square algorithm.

def rand_fn():
    return random.random() - 0.5

def diamond_square(z, x, y, w):
    nw = w/2

    # Center.
    ave = 0.25 * (z[x,y] + z[x, y+w] + z[x+w,y] + z[x+w,y+w])    
    z[x+nw, y+nw] = ave + float(nw) * rand_fn()

    # Edges.
    for [ex, ey] in [[x + nw, y], [x, y + nw], [x + w, y + nw], [x + nw, y + w]]:
        ave = 0.0
        cnts = 0
        for [dx, dy] in [[0, -nw], [-nw, 0], [nw, 0], [0, nw]]:
            tx = ex + dx
            ty = ey + dy
            if (tx > -1) and (tx <= l_size) and (ty > -1) and (ty <= l_size):
                ave += z[tx, ty]
                cnts += 1
        z[ex, ey] = ave/float(cnts) + (float(nw) / math.sqrt(2)) * (random.random() - 0.5)

# 1, 3, 6, 10 are interesting.
random.seed(3)

#l_size = 64
l_size = 32
landscape = numpy.zeros((l_size + 1, l_size + 1))
landscape[0,0] = float(l_size) * rand_fn()
landscape[0,-1] = float(l_size) * rand_fn()
landscape[-1,0] = float(l_size) * rand_fn()
landscape[-1,-1] = float(l_size) * rand_fn()

c_size = l_size
while(c_size > 1):
    x = 0
    while (x < l_size):
        y = 0
        while (y < l_size):
            diamond_square(landscape, x, y, c_size)
            y += c_size
        x += c_size
    c_size = c_size / 2

# Set negative values to 0.0 (for ocean)
landscape[(landscape < 0)] = 0.0

# Output text parts file.
#
# 3005 for 1 x 1 brick.
# 30008 for 1 x 1 plate.
#
# 1, Blue.
# 2, Green.
# 6, Brown
# 15, White.

print numpy.max(landscape)

def addBrick(fp, x, y, z, color, stop):
    while (z < stop):
        if ((z + 2) < stop):
            fp.write(str(i) + " " + str(j) + " " + str(disp*(z+2)) + " -90 0 0 3005 " + color + "\n")
        z += 3

    if (z > stop):
        z -= 3
        
    while (z < stop):
        fp.write(str(i) + " " + str(j) + " " + str(disp*z) + " -90 0 0 30008 " + color + "\n")
        z += 1

    return z
             
disp = 1.0/3.0
with open("landscape.txt", "w") as fp:
    for i in range(l_size+1):
        for j in range(l_size+1):
            if (landscape[i,j] == 0.0):
                fp.write(str(i) + " " + str(j) + " 0 -90 0 0 30008 1\n")
            else:
                g_bd = 10 + random.randrange(3)
                b_bd = g_bd + 2 + random.randrange(2)
                z_max = int(5.0 * landscape[i,j])
                if (z_max == 0):
                    fp.write(str(i) + " " + str(j) + " 0 -90 0 0 30008 2\n")
                else:
                    z = 0
                    if (z_max < g_bd):
                        addBrick(fp, x, y, z, "2", z_max)
                        continue
                    else:
                        z = addBrick(fp, x, y, z, "2", g_bd)

                    if (z_max < b_bd):
                        addBrick(fp, x, y, z, "6", z_max)
                        continue
                    else:
                        z = addBrick(fp, x, y, z, "6", b_bd)
                        
                    addBrick(fp, x, y, z, "15", z_max)

if 0:
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import axes3d

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    grid = numpy.indices((l_size+1, l_size+1))
    ax.plot_wireframe(grid[0], grid[1], landscape, rstride=1, cstride=1)

    #print grid[0], grid[1]
    plt.show()


