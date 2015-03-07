#!/usr/bin/env python
"""
.. module:: chain
   :synopsis: The chain function.

.. moduleauthor:: Hazen Babcock

"""

import math
import numbers
import numpy

import angles
import functions
import interpreter as interp
import lcadExceptions

lcad_functions = {}


#
# These classes create a chain function that can be used in opensdraw.
#
class ChainFunction(functions.LCadFunction):

    def __init__(self, chain):
        functions.LCadFunction.__init__(self, "user created chain function")
        self.chain = chain

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


class LCadChain(functions.LCadFunction):
    """
    **chain** - Creates a chain function.
    
    This function creates and returns a function that parametrizes a chain,
    making it easier to add chains, tracks, etc. to a MOC. All units are LDU.
    A chain must have at least two sprockets. Each sprocket is specified by 
    a 4 member list consisting of *(x y radius winding-direction)*, where 
    winding-direction specifies which way the chain goes around the sprocket 
    (1 = counter-clockwise, -1 = clockwise). The chain goes around the sprockets
    in the order in which they are specified, and when *:continuous* is t
    returns from the last sprocket to the first sprocket to close the loop.

    When you call the created chain function you will get a 6 element list 
    *(x y z rx ry rz)*. Since (currently) the chain is in the x-y plane, z will 
    always be zero. The angles rx, ry and rz will rotate the coordinate system
    such that the z-axis is pointing along the chain the y-axis is in the plane
    of the chain and the x-axis is perpendicular to the plane of the chain.

    If you call the created chain function with the argument **t** it will return the 
    length of the chain.

    Additionally chain has the keyword argument::

      :continuous t/nil  ; The default is t, distances will be interpreted modulo the chain length, and
                         ; the chain will go from that last sprocket back to the first sprocket. If nil
                         ; then negative distances will wrap around the first sprocket and positive
                         ; distances will wrap around the last sprocket.

    Usage::

     (def a-chain (chain (list (list -4 0 1 1)    ; Create a chain with two sprockets, the 1st at (-4,0) and
                               (list 4 0 1 1))))  ; the second at (4,0). Both sprockets have radius 1 and a
                                                  ; counter-clockwise winding direction.
     (def c1 (a-chain 1))                         ; c1 is the list (x y z rx ry rz).
     (a-chain t)                                  ; Returns the length of the chain.

    """
    def __init__(self):
        functions.LCadFunction.__init__(self, "chain")

    def argCheck(self, tree):
        if (len(tree.value) < 2):
            raise lcadExceptions.NumberArgumentsException(len(tree.value)-1)

        # Check keyword arguments.
        if (len(tree.value) > 2):
            args = tree.value[2:]
            index = 0
            while (index < len(args)):
                arg = args[index]
            
                if (arg.value[0] == ":"):
                    if not (arg.value in [":continuous"]):
                        raise lcadExceptions.UnknownKeywordException(arg.value)
                    index += 2
                    if (index > len(args)):
                        raise lcadExceptions.KeywordValueException()
                else:
                    raise lcadExceptions.KeywordException(arg.value)


    def call(self, model, tree):

        # Keyword defaults.
        continuous = True

        # Get list of sprockets.
        sprocket_list = interp.getv(interp.interpret(model, tree.value[1:]))

        if not isinstance(sprocket_list, interp.List):
            raise lcadExceptions.WrongTypeException("list", type(sprocket_list))

        if (sprocket_list.size < 2):
            raise NumberSprocketsException(sprocket_list.size)

        # Process keywords.
        index = 0
        args = tree.value[2:]
        while (index < len(args)):
            arg = args[index]

            # Process keyword.
            if (arg.value == ":continuous"):
                continuous = functions.isTrue(model, args[index+1])
            index += 2

        # Create sprockets.
        sprockets = []
        for i in range(sprocket_list.size):
        
            sprocket = interp.getv(sprocket_list.getv(i))

            if not isinstance(sprocket, interp.List):
                raise lcadExceptions.WrongTypeException("list", type(sprocket))

            if (sprocket.size != 4):
                raise SprocketException(sprocket.size)

            vals = []
            for j in range(4):
                val = interp.getv(sprocket.getv(j))
                if not isinstance(val, numbers.Number):
                    raise lcadExceptions.WrongTypeException("number", type(val))
                vals.append(val)
            sprockets.append(Sprocket(*vals))

        # Create chain.
        for i in range(len(sprockets)-1):
            sprockets[i].addNextSprocket(sprockets[i+1])
        sprockets[-1].addNextSprocket(sprockets[0])

        chain = Chain(continuous)
        for sprocket in sprockets:
            sprocket.addToChain(chain)
        chain.finishChain()

        # Return chain function.
        return ChainFunction(chain)

lcad_functions["chain"] = LCadChain()

        
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

    def __init__(self, continuous):
        self.chain_length = 0
        self.chain = []
        self.continuous = continuous
        self.first_sprocket = None
        self.last_sprocket = None

    def addSegment(self, d, x, y, theta):
        self.chain_length += d
        self.chain.append(ChainSegment(self.chain_length, x, y, theta))

    def finishChain(self):
        """
        Add segment to connect the end of the chain back to the beginning.
        """
        if self.continuous:
            dx = self.chain[-1].x - self.chain[0].x
            dy = self.chain[-1].y - self.chain[0].y
            self.addSegment(math.sqrt(dx*dx + dy*dy),
                            self.chain[0].x,
                            self.chain[0].y,
                            self.chain[0].theta)

    def getAngles(self, theta):

        # Solve for angles to rotate into a frame with z along the 
        # chain, y in the plane of the chain and x pointing up.

        x_vec = numpy.array([0,0,1])
        y_vec = numpy.array([math.cos(theta - 0.5 * math.pi), 
                             math.sin(theta - 0.5 * math.pi),
                             0])
        z_vec = numpy.array([math.cos(theta), 
                             math.sin(theta),
                             0])
        return angles.vectorsToAngles(x_vec, y_vec, z_vec)

    def getLen(self):
        return len(self.chain)

    def getPositionOrientation(self, distance):
        """
        Return the position and orientation for a segment at distance along the chain.
        distance is modulo the chain length.
        """

        # Modulo d.
        if self.continuous:
            while (distance < 0):
                distance += self.chain_length
            while (distance > self.chain_length):
                distance -= self.chain_length
        else:
            if (distance < 0):
                # Go backwards around the first sprocket.
                sprocket = self.first_sprocket
                d_angle = abs(distance)/sprocket.r
                if (sprocket.winding == 1):
                    angle = sprocket.start_angle - d_angle
                    [rx, ry, rz] = self.getAngles(angle + 0.5 * math.pi)
                    return [sprocket.x + sprocket.r * math.cos(angle),
                            sprocket.y + sprocket.r * math.sin(angle), 0,
                            rx, ry, rz]
                else:
                    angle = sprocket.start_angle + d_angle
                    [rx, ry, rz] = self.getAngles(angle - 0.5 * math.pi)
                    return [sprocket.x + sprocket.r * math.cos(angle),
                            sprocket.y + sprocket.r * math.sin(angle), 0,
                            rx, ry, rz]

            elif (distance > self.chain_length):
                print "off", distance

                # Go forwards around the last sprocket.
                sprocket = self.last_sprocket
                d_angle = abs(distance - self.chain_length)/sprocket.r
                if (sprocket.winding == 1):
                    angle = sprocket.end_angle + d_angle
                    [rx, ry, rz] = self.getAngles(angle + 0.5 * math.pi)
                    return [sprocket.x + sprocket.r * math.cos(angle),
                            sprocket.y + sprocket.r * math.sin(angle), 0,
                            rx, ry, rz]
                else:
                    angle = sprocket.end_angle - d_angle
                    [rx, ry, rz] = self.getAngles(angle - 0.5 * math.pi)
                    return [sprocket.x + sprocket.r * math.cos(angle),
                            sprocket.y + sprocket.r * math.sin(angle), 0,
                            rz, ry, rz]

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

        [rx, ry, rz] = self.getAngles(ftheta)

        return [self.chain[start].x + dx,
                self.chain[start].y + dy,
                0, rx, ry, rz]


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

        # Keep track of first and last sprockets for continuous = False.
        if a_chain.first_sprocket is None:
            a_chain.first_sprocket = self
        else:
            a_chain.last_sprocket = self

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

        #if (a_chain.continuous is False) and (a_chain.getLen() == 1):
        #    return

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
    s3 = Sprocket(0,-1.5,1,-1)
    s1.addNextSprocket(s2)
    s2.addNextSprocket(s3)
    s3.addNextSprocket(s1)

    chain = Chain(True)
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
    #circle3=plt.Circle((s3.x,s3.y),s3.r, fc='none', ec='b')
    fig = plt.gcf()
    fig.gca().add_artist(circle1)
    fig.gca().add_artist(circle2)
    #fig.gca().add_artist(circle3)

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
        for i in range(23):
            [x, y, z, rx, ry, rz] = chain.getPositionOrientation(i - 3)
            dx = math.cos(rz * math.pi/180.0)
            dy = math.sin(rz * math.pi/180.0)
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
