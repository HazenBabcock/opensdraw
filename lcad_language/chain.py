#!/usr/bin/env python
"""
.. module:: chain
   :synopsis: The chain function.

.. moduleauthor:: Hazen Babcock

"""

import math
import numbers
import numpy

import functions
import interpreter as interp
import lcadExceptions

builtin_functions = {}


#
# These classes create a chain function that can be used in openldraw.
#
class ChainFunction(functions.LCadFunction):

    def __init__(self, chain):
        self.chain = chain
        self.name = "user created chain function"

    def argCheck(self, tree):
        if (len(tree.value) != 2):
            raise lcadExceptions.NumberArgumentsException("1", len(tree.value) - 1)

    def call(self, model, tree):
        arg = interp.getv(interp.interpret(model, tree.value[1]))

        # If arg is t return the curve length.
        if (arg is interp.lcad_t):
            return self.chain.chain_length        

        # Get distance along chain.
        if not isinstance(arg, numbers.Number):
            raise lcadExceptions.WrongTypeException("number", type(arg))

        # Determine position and orientation.
        return interp.List(self.chain.getPositionOrientation(arg))


class LCadChain(functions.SpecialFunction):
    """
    **chain** - Creates a chain function.
    
    This function creates and returns a function that parametrizes a chain,
    making it easier to add chains, tracks, etc. to a MOC. All units are LDU.
    A chain must have at least two sprockets. Each sprocket is specified by 
    a 4 member list consisting of (x y radius winding-direction), where 
    winding-direction specifies which way the chain goes around the sprocket 
    (1 = counter-clockwise, -1 = clockwise). The chain goes around the sprockets
    in the order in which they are specified, and returns from the last sprocket
    to the first sprocket to close the loop.

    When you call the created chain function you will get a 3 element list 
    (x y theta). The distance argument that is provided to created chain function
    will be adjusted to be modulo the length of the chain.

    If you call the created chain function with the argument t it will return the 
    length of the chain.

    Usage::

     (def a-chain (chain (-4 0 1 1) (4 0 1 1)))  ; Create a chain with two sprockets, the 1st at (-4,0) and
                                                 ; the second at (4,0). Both sprockets have radius 1 and a
                                                 ; counter-clockwise winding direction.
     (def c1 (a-chain 1))                        ; c1 is the list (x y theta), where x,y are position and 
                                                 ; theta is the orientation (in degrees).
     (a-chain t)                                 ; Returns the length of the chain.

    """
    def __init__(self):
        self.name = "chain"

    def argCheck(self, tree):

        # Check for at least two sprockets.
        if (len(tree.value) < 3):
            raise NumberSprocketsException(len(tree.value)-1)

        # Check that there are four arguments per sprocket.
        args = tree.value[1:]
        for arg in args:
            if not isinstance(arg.value, list):
                raise SprocketException(1)
            if (len(arg.value) != 4):
                raise SprocketException(len(arg.value))

    def call(self, model, tree):
        args = tree.value[1:]

        # Create sprockets.
        sprockets = []
        for arg in args:
            vals = []
            for i in range(4):
                val = interp.getv(interp.interpret(model, arg.value[i]))
                if not isinstance(val, numbers.Number):
                    raise lcadExceptions.WrongTypeException("number", type(val))
                vals.append(val)
            sprockets.append(Sprocket(*vals))

        # Create chain.
        for i in range(len(sprockets)-1):
            sprockets[i].addNextSprocket(sprockets[i+1])
        sprockets[-1].addNextSprocket(sprockets[0])

        chain = Chain()
        for sprocket in sprockets:
            sprocket.addToChain(chain)
        chain.finishChain()

        # Return chain function.
        return ChainFunction(chain)

builtin_functions["chain"] = LCadChain()

        
class NumberSprocketsException(lcadExceptions.LCadException):
    def __init__(self, got):
        lcadExceptions.LCadException.__init__(self, "A chain must have 2 sprockets, got " + str(got))


class SprocketException(lcadExceptions.LCadException):
    def __init__(self, got):
        lcadExceptions.LCadException.__init__(self, "A sprocket must have 4 arguments, got " + str(got))


#
# The classes below do the math necessary to create a chain.
#
class Chain(object):

    def __init__(self):
        self.chain_length = 0
        self.chain = []

    def addSegment(self, d, x, y, theta):
        self.chain_length += d
        self.chain.append(ChainSegment(self.chain_length, x, y, theta))

    def finishChain(self):
        """
        Add segment to connect the end of the chain back to the beginning.
        """
        dx = self.chain[-1].x - self.chain[0].x
        dy = self.chain[-1].y - self.chain[0].y
        self.addSegment(math.sqrt(dx*dx + dy*dy),
                        self.chain[0].x,
                        self.chain[0].y,
                        self.chain[0].theta)
        #print self.chain_length

    def getLen(self):
        return len(self.chain)

    def getPositionOrientation(self, distance):
        """
        Return the position and orientation for a segment at distance along the chain.
        distance is modulo the chain length.
        """

        # Modulo d.
        while (distance < 0):
            distance += self.chain_length
        while (distance > self.chain_length):
            distance -= self.chain_length

        # Mid-point bisection to find the bracketing chain segments.
        start = 0
        end = len(self.chain)-1
        mid = (end - start)/2
        while ((end - start) > 1):
            if (distance > self.chain[mid].d):
                start = mid
            elif (distance == self.chain[mid].d):
                start = mid
                end = start + 1
                #if (end == len(self.chain)):
                #    end = 0
            else:
                end = mid
            mid = (end - start)/2 + start

        # Interpolate between the two segments.
        normed_d = (distance - self.chain[start].d)/(self.chain[end].d - self.chain[start].d)
        dx = normed_d * (self.chain[end].x - self.chain[start].x)
        dy = normed_d * (self.chain[end].y - self.chain[start].y)

        # Adjust angles so that we can properly interpolate the angles.
        theta1 = self.chain[start].theta
        theta2 = self.chain[end].theta
        while ((theta2 - theta1) > math.pi):
            theta1 += 2.0 * math.pi
        while ((theta2 - theta1) < -math.pi):
            theta1 -= 2.0 * math.pi
        dtheta = normed_d * (theta2 - theta1)

        # Modulo angle to 2pi.
        ftheta = (self.chain[start].theta + dtheta)
        while (ftheta > (2.0 * math.pi)):
            ftheta -= 2.0 * math.pi
        while (ftheta < 0.0):
            ftheta += 2.0 * math.pi

        return [self.chain[start].x + dx,
                self.chain[start].y + dy,
                ftheta * 180.0/math.pi]


class ChainSegment(object):

    def __init__(self, d, x, y, theta):
        self.d = d          # The distance along the chain of this particular segment in LDU.
        self.x = x          # The x position of the segment in LDU.
        self.y = y          # The y position of the segment in LDU.
        self.theta = theta  # The angle in the XY plane of the vector that is normal to the segment.


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
        #print ori

        self.end_angle += ori
        a_sprocket.start_angle += ori
        
        t_dx = self.chain_dx
        t_dy = self.chain_dy
        self.chain_dx = t_dx * math.cos(ori) - t_dy * math.sin(ori)
        self.chain_dy = t_dx * math.sin(ori) + t_dy * math.cos(ori)

    def addToChain(self, a_chain):
        """
        Add segments for this sprocket to the chain.
        """

        # Adjust end angle based on winding. Basically we want the end angle 
        # to be 0 - 2pi ahead of the start angle in the winding direction.
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

        #print self.start_angle, self.end_angle

        # Add first segment.
        x = self.x + self.r * math.cos(self.start_angle)
        y = self.y + self.r * math.sin(self.start_angle)

        distance = 0
        if not (a_chain.getLen() == 0):
            dx = x - a_chain.chain[-1].x
            dy = y - a_chain.chain[-1].y
            distance = math.sqrt(dx*dx + dy*dy)

        if (self.winding == 1):
            a_chain.addSegment(distance, x, y, self.start_angle + 0.5 * math.pi)
        else:
            a_chain.addSegment(distance, x, y, self.start_angle - 0.5 * math.pi)

        # Add additional segments.
        d_angle = math.pi/180.0
        d_distance = math.pi * self.r/180.0
        if (self.winding == 1):
            angle = self.start_angle + d_angle
            while (angle < self.end_angle):
                a_chain.addSegment(d_distance,
                                   self.x + self.r * math.cos(angle),
                                   self.y + self.r * math.sin(angle),
                                   angle + 0.5 * math.pi)
                angle += d_angle
            angle -= d_angle
            distance = (self.end_angle - angle) * self.r
        else:
            angle = self.start_angle - d_angle
            while (angle > self.end_angle):
                a_chain.addSegment(d_distance,
                                   self.x + self.r * math.cos(angle),
                                   self.y + self.r * math.sin(angle),
                                   angle - 0.5 * math.pi)
                angle -= d_angle
            angle += d_angle
            distance = (angle - self.end_angle) * self.r

        # Add final segment.
        if (self.winding == 1):
            a_chain.addSegment(distance,
                               self.x + self.r * math.cos(self.end_angle),
                               self.y + self.r * math.sin(self.end_angle),
                               self.end_angle + 0.5 * math.pi)
        else:
            a_chain.addSegment(distance,
                               self.x + self.r * math.cos(self.end_angle),
                               self.y + self.r * math.sin(self.end_angle),
                               self.end_angle - 0.5 * math.pi)


#
# Testing
#
if (__name__ == "__main__"):

    s1 = Sprocket(-4,0,1.5,-1)
    s2 = Sprocket(4,0,1.5,-1)
    s3 = Sprocket(0,-1.5,1,1)
    s1.addNextSprocket(s2)
    s2.addNextSprocket(s3)
    s3.addNextSprocket(s1)

    chain = Chain()
    s1.addToChain(chain)
    s2.addToChain(chain)
    s3.addToChain(chain)
    chain.finishChain()

    # Create plot.
    import matplotlib.pyplot as plt
    ax = plt.axes(aspect = 1)

    # Sprockets.
    circle1=plt.Circle((s1.x,s1.y),s1.r, fc='none', ec='b')
    circle2=plt.Circle((s2.x,s2.y),s2.r, fc='none', ec='b')
    circle3=plt.Circle((s3.x,s3.y),s3.r, fc='none', ec='b')
    fig = plt.gcf()
    fig.gca().add_artist(circle1)
    fig.gca().add_artist(circle2)
    fig.gca().add_artist(circle3)

    if 0:
        # Chain.
        ax.arrow(s1.r * math.cos(s1.end_angle) + s1.x,
                 s1.r * math.sin(s1.end_angle) + s1.y,
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

    if 1:
        for i in range(50):
            [x, y, theta] = chain.getPositionOrientation(0.5*i)
            #dx = math.cos(theta)
            #dy = math.sin(theta)
            dx = math.cos(theta * math.pi/180.0)
            dy = math.sin(theta * math.pi/180.0)
            ax.arrow(x, y, dx, dy, head_width=0.05, head_length=0.1, fc='k', ec='k')
    
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
