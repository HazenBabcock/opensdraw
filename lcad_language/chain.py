#!/usr/bin/env python
"""
.. module:: chain
   :synopsis: The chain function.

.. moduleauthor:: Hazen Babcock

"""

import math

class ChainSegment(object):

    def __init__(self, d, x, y, theta):
        self.d = d          # The distance along the chain of this particular segment in LDU.
        self.x = x          # The x position of the segment in LDU.
        self.y = y          # The y position of the segment in LDU.
        self.theta = theta  # The orientation of the segment in LDU.

class Sprocket(object):

    def __init__(self, x, y, r, winding):
        self.x = x              # Sprocket x position in LDU.
        self.y = y              # Sprocket y position in LDU.
        self.r = r              # Sprocket radius.
        self.winding = winding  # Winding direction (1 = CCW, -1 == CW).

        self.start_angle = 0    # The angle at which the chain enters the sprocket.
        self.end_angle = 0      # The angle at which the chain leaves the sprocket.
        self.chain_dx = 0       # The dx value for a chain between the two sprockets.
        self.chain_dy = 0       # The dy value for a chain between the two sprockets.

    def addNextSprocket(self, a_sprocket):
        """
        Figures out the angles and vector for the chain that
        connects this sprocket to the next sprocket.
        """

        dx = a_sprocket.x - self.x
        dy = a_sprocket.y - self.y
        dd = math.sqrt(dx*dx + dy*dy)

        if (dd < (self.r + a_sprocket.r)):
            print "Warning! Sprockets overlap!"

        # Do calculations in a coordinate system where the x-axis
        # is the line between the centers of the two sprockets.
        if (self.winding == a_sprocket.winding):
            rho = math.asin((a_sprocket.r - self.r) / dd)
            phi = 0.5 * math.pi + rho
            chain_length = dd * math.cos(rho)
            self.chain_dx = chain_length * math.cos(rho)
            self.chain_dy = chain_length * math.sin(rho)

            if (self.winding == 1):
                self.end_angle = 2.0 * math.pi - phi
                a_sprocket.start_angle = 2.0 * math.pi - phi
                self.chain_dy = -self.chain_dy
            else:
                self.end_angle = phi
                a_sprocket.start_angle = phi
        else:
            phi = math.acos((a_sprocket.r + self.r)/dd)
            chain_length = dd * math.sin(phi)
            rho = phi - 0.5*math.pi
            self.chain_dx = chain_length * math.cos(rho)
            self.chain_dy = chain_length * math.sin(rho)

            if (self.winding == 1):
                self.end_angle = -phi
                a_sprocket.start_angle = math.pi - phi
                self.chain_dy = -self.chain_dy
            else:
                self.end_angle = phi
                a_sprocket.start_angle = math.pi + phi

        # Rotate results into the actual coordinate system.
        ori = math.atan2(dy, dx)
        print ori

        self.end_angle += ori
        a_sprocket.start_angle += ori
        
        t_dx = self.chain_dx
        t_dy = self.chain_dy
        self.chain_dx = t_dx * math.cos(ori) - t_dy * math.sin(ori)
        self.chain_dy = t_dx * math.sin(ori) + t_dy * math.cos(ori)

        # Adjust end angle based on winding for later processing convenience.
        # Basically we want the end angle to be 0 - 2pi ahead of the start angle in the winding direction.
        if (self.winding == 1):
            while (self.end_angle > (self.start_angle + 2.0 * math.pi)):
                self.end_angle -= 2.0 * math.pi
            while (self.end_angle < self.start_angle):
                self.end_angle += 2.0 * math.pi
        else:
            while (self.end_angle > self.start_angle):
                self.end_angle -= 2.0 * math.pi
            while (self.end_angle < (self.start_angle - 2.0 * math.pi)):
                self.end_angle += 2.0 * math.pi

    def addToChain(self, chain):

        # Add first segment.
        x = self.x + self.r * math.cos(self.start_angle)
        y = self.y + self.r * math.sin(self.start_angle)
        if (self.winding == 1):
            theta = self.start_angle + 0.5 * math.pi
        else:
            theta = self.start_angle - 0.5 * math.pi

        d = 0
        if not (len(chain) == 0):
            dx = x - chain[-1].x
            dy = y - chain[-1].y
            d = math.sqrt(dx*dx + dy*dy) + chain[-1].d

        chain.append(ChainSegment(d,x,y,theta))

        # Add additional segments.
        angle = start_angle
        if (self.winding == 1):
            while(

#
# Testing
#
if (__name__ == "__main__"):

    s1 = Sprocket(0,0,1,1)
    s2 = Sprocket(-4,-2,0.5,-1)
    s1.addNextSprocket(s2)

    # Create plot.
    import matplotlib.pyplot as plt
    ax = plt.axes(aspect = 1)

    # Sprockets.
    circle1=plt.Circle((s1.x,s1.y),s1.r, fc='none', ec='b')
    circle2=plt.Circle((s2.x,s2.y),s2.r, fc='none', ec='b')
    fig = plt.gcf()
    fig.gca().add_artist(circle1)
    fig.gca().add_artist(circle2)

    # Chain.
    ax.arrow(s1.r * math.cos(s1.end_angle),
             s1.r * math.sin(s1.end_angle),
             s1.chain_dx,
             s1.chain_dy,
             head_width=0.05, head_length=0.1, fc='k', ec='k')

    # Show start & end angles.
    ax.arrow(s1.x,
             s1.y,
             s1.r * math.cos(s1.end_angle),
             s1.r * math.sin(s1.end_angle),
             head_width=0.05, head_length=0.1, fc='k', ec='k')
    ax.arrow(s2.x,
             s2.y,
             s2.r * math.cos(s2.start_angle),
             s2.r * math.sin(s2.start_angle),
             head_width=0.05, head_length=0.1, fc='k', ec='k')

    ax.set_xlim([-10,10])
    ax.set_ylim([-10,10])

    plt.show()

    #print s1.end_angle
    #print s2.start_angle


#
# The MIT License
#
# Copyright (c) 2014 Hazen Babcock
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
