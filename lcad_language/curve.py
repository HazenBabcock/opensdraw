#!/usr/bin/env python
"""
.. module:: curve
   :synopsis: The curve function.

.. moduleauthor:: Hazen Babcock

"""

import math
import numbers
import numpy

import functions
import interpreter as interp
import lcadExceptions

lcad_functions = {}


#
# These classes create a curve function that can be used in openldraw.
#
class CurveFunction(functions.LCadFunction):

    def __init__(self, curve):
        functions.LCadFunction.__init__(self, "user created curve function")
        self.curve = curve

    def argCheck(self, tree):
        if (len(tree.value) != 2):
            raise lcadExceptions.NumberArgumentsException("1", len(tree.value) - 1)

    def call(self, model, tree):
        arg = interp.getv(interp.interpret(model, tree.value[1]))

        # If arg is t return the curve length.
        if (arg is interp.lcad_t):
            return self.curve.length

        # Get distance along curve.
        if not isinstance(arg, numbers.Number):
            raise lcadExceptions.WrongTypeException("number", type(arg))

        # Determine position and orientation.
        return interp.List(self.curve.getCoords(arg))


class Curve(functions.LCadFunction):
    """
    **curve** - Creates a curve function.
    
    This function creates and returns a function that parametrizes a curve, specifically
    a cubic spline. All units are LDU. Each control point is specified by a list of lists
    in the form *((xp yp zp) (dx dy dz))*, where xp, yp and zp specify the location of the
    control point and dx, dy, dz specify the derivative (tangent) of the line as it 
    passes through the control point. A curve must have at least two control points, and
    additionally you must provide a (approximately) perpendicular vector to the
    derivate *((xp yp zp) (dx dy dz) (px py pz))* for the first control point.

    When you call the created curve function you will get the 6 element list *(x y z rx ry rz)* 
    where x, y, z are the location of the curve and rx, ry, rz are the angles that will rotate
    from the current coordinate system to the curve coordinate system. In the curve
    coordinate system z is along the curve and x is perpendicular to the coordinate system
    as defined by the perpendicular vector provided for the 1st control point. The distance
    argument to the created curve function will be adjusted to be in the range 0 - curve
    length if the argument falls outside of this range.

    If you call the created curve function with the argument **t** it will return the length
    of the curve.

    Additionally curve has several keyword arguments::

      :auto-scale   t/nil        ; default is t, automatically scale the derivative.
      :extrapolate  t/nil        ; default is t, distances outside of the curve will be
                                 ; linearly extrapolated from the end of the curve. If nil
                                 ; then the distance will be modulo the curve length.
      :scale        float > 0.0  ; multiplier for auto-scale mode, defaults to 1.
      :twist        angle        ; additional twist along the curve, defaults to 0.


    Usage::

     (def my-curve (curve ((0 0 0) (1 1 0) (0 0 1)) ; Create a curve going through (0,0,0), (5,0,0)
                          ((5 0 0) (1 0 0))))       ; With derivative (1,1,0) and (1,0,0). Since we did
                                                    ; not specify :auto-scale nil, the derivative will
                                                    ; be scaled to create a hopefully pleasing curve.

     (def p1 (my-curve 1))                          ; p1 is the list (x y z rx ry rz) which defines the
                                                    ; curve at distance one along the curve.
     (my-curve t)                                   ; Returns the length of the curve.

    """
    def __init__(self):
        functions.LCadFunction.__init__(self, "curve")

    def argCheck(self, tree):
        
        # Check for at least two control points.
        if (len(tree.value) < 3):
            raise NumberControlPointsException(len(tree.value)-1)

        # Check for 3 x 2 or (3 x 3) arguments per control point.
        # Keyword arguments come after control points.
        args = tree.value[1:]
        index = 0
        n_control_points = 0
        while (index < len(args)):
            arg = args[index]
            
            # Check if argument is a keyword.
            if not isinstance(arg.value, list):
                if (arg.value[0] == ":"):
                    if (n_control_points < 2):
                        raise NumberControlPointsException(n_control_points)
                    if not (arg.value in [":auto-scale", ":extrapolate", ":scale", ":twist"]):
                        raise lcadExceptions.UnknownKeywordException(arg.value)
                    index += 2
                    if (index > len(args)):
                        raise lcadExceptions.KeywordValueException()
                    continue
                else:
                    raise ControlPointException(arg.value + " is not a list or a keyword")

            # If it is a list, check that it is properly composed.
            if not isinstance(arg.value, list):
                raise ControlPointException("Argument must be a list of lists")
            if (index == 0):
                if (len(arg.value) != 3):
                    raise ControlPointException("First control point must include a perpendicular vector.")
            else:
                if (len(arg.value) != 2):
                    raise ControlPointException("Control point must include only a location and a derivative (tangent) vector.")

            # Check that the sub-lists have the right number of arguments.
            for vec in arg.value:
                if not isinstance(vec.value, list):
                    raise ControlPointException("Argument must be a list")
                if (len(vec.value) != 3):
                    raise ControlPointException("List must have 3 elements")
            
            n_control_points += 1
            index += 1

    def call(self, model, tree):
        args = tree.value[1:]

        auto_scale = True
        extrapolate = True
        scale = 1.0
        twist = 0.0

        # Create control points.
        index = 0
        control_points = []
        while (index < len(args)):
            arg = args[index]

            # Process keyword.
            if not isinstance(arg.value, list):
                if (arg.value == ":auto-scale"):
                    auto_scale = functions.isTrue(model, args[index+1])
                if (arg.value == ":extrapolate"):
                    extrapolate = functions.isTrue(model, args[index+1])
                if (arg.value == ":scale"):
                    scale = interp.getv(interp.interpret(model, args[index+1]))
                    if not isinstance(scale, numbers.Number):
                        raise lcadExceptions.WrongTypeException("number", type(scale))
                if (arg.value == ":twist"):
                    twist = interp.getv(interp.interpret(model, args[index+1]))
                    if not isinstance(twist, numbers.Number):
                        raise lcadExceptions.WrongTypeException("number", type(twist))
                index += 2
                continue

            # Create control point.
            vals = []
            for vec in arg.value:
                for i in range(3):
                    val = interp.getv(interp.interpret(model, vec.value[i]))
                    if not isinstance(val, numbers.Number):
                        raise lcadExceptions.WrongTypeException("number", type(val))
                    vals.append(val)
            control_points.append(ControlPoint(*vals))
            index += 1

        # Create curve.
        curve = Curve(auto_scale, extrapolate, scale, twist)
        for i in range(len(control_points)-1):
            curve.addSegment(control_points[i], control_points[i+1])

        # Return curve function.
        return CurveFunction(curve)

lcad_functions["curve"] = Curve()


class ControlPointException(lcadExceptions.LCadException):
    def __init__(self, msg):
        lcadExceptions.LCadException.__init__(self, msg)
        

class NumberControlPointsException(lcadExceptions.LCadException):
    def __init__(self, got):
        lcadExceptions.LCadException.__init__(self, "A curve must have at least 2 control points, got " + str(got))


class TangentException(lcadExceptions.LCadException):
    def __init__(self):
        lcadExceptions.LCadException.__init__(self, "The length of the tangent line must be greater than 0.")


#
# The classes below do the math necessary to create a curve.
#
# In the curve coordinate system the z vector is the tangent to the
# curve and x/y vectors are perpendicular to the curve.
#

def crossProduct(u, v):
    cp = numpy.zeros(3)
    cp[0] = u[1]*v[2] - u[2]*v[1]
    cp[1] = u[2]*v[0] - u[0]*v[2]
    cp[2] = u[0]*v[1] - u[1]*v[0]
    return cp

def dotpVector(v1, v2):
    return numpy.sum(v1 * v2)

def normVector(vector):
    return vector/numpy.sqrt(numpy.sum(vector * vector))

# Return the projection of vector1 onto vector2.
def projVector(v1, v2):
    return numpy.dot(v1, v2) * v2

def toDegrees(angle):
    return 180.0 * angle/math.pi


class ControlPoint(object):

    def __init__(self, x, y, z, dx, dy, dz, px = 0, py = 0, pz = 0):
        
        self.location = numpy.array([x, y, z])
        self.raw_z_vec = numpy.array([dx, dy, dz])
        self.x_vec = numpy.array([px, py, pz])

        if (dotpVector(self.raw_z_vec, self.raw_z_vec) == 0.0):
            raise TangentException

        self.z_vec = normVector(self.raw_z_vec)

        # Only the first point has a perpendicular vector.
        if (dotpVector(self.x_vec, self.x_vec) > 0.1):

            # Normalize perpendicular vector.
            self.x_vec = normVector(self.x_vec)
            
            # Adjust x_vec to make it exactly perpendicular to z_vec
            # and normalize it's length to one.
            self.x_vec = normVector(self.x_vec - projVector(self.z_vec, self.x_vec))

            # Compute cross-product of z_vec and x_vec to create y vector.
            #cpx = self.z_vec[1]*self.x_vec[2] - self.z_vec[2]*self.x_vec[1]
            #cpy = self.z_vec[2]*self.x_vec[0] - self.z_vec[0]*self.x_vec[2]
            #cpz = self.z_vec[0]*self.x_vec[1] - self.z_vec[1]*self.x_vec[0]
            #self.y_vec = numpy.array([cpx, cpy, cpz])
            self.y_vec = crossProduct(self.z_vec, self.x_vec)

        else:
            self.x_vec = None
            self.y_vec = None


class Curve(object):

    def __init__(self, normalize, extrapolate, scale, total_twist):
        self.extrapolate = extrapolate
        self.length = 0
        self.normalize = normalize
        self.scale = scale
        self.segments = []
        self.total_twist = total_twist

    def addSegment(self, control_point_1, control_point_2):
        segment = Segment(control_point_1, control_point_2, self.normalize, self.scale, self.length)
        self.segments.append(segment)
        self.length += segment.length

    def getCoords(self, dist):

        if not self.extrapolate:
            while (dist < 0):
                dist += self.length
            while (dist > self.length):
                dist -= self.length

        if (dist < 0):
            a_seg = self.segments[0]
        elif (dist > self.length):
            a_seg = self.segments[-1]
        else:
            for seg in self.segments:
                if (dist >= seg.dist_lut[0][1]) and (dist <= seg.dist_lut[-1][1]):
                    a_seg = seg
                    break
            
        # Get position and angles.
        [x, y, z, rx, ry, rz] = a_seg.getCoords(dist)

        # Add twist to the z angle.
        rz += self.total_twist * (dist / self.length)
        return [x, y, z, rx, ry, rz]
                

class Segment(object):

    def __init__(self, control_point_1, control_point_2, normalize, scale, dist_offset):

        # Control point 1 is assumed to have a valid perpendicular (x_vec).
        # Control point 2 will be modified to have a valid (non-zero) x_vec.
        self.cp1 = control_point_1
        self.cp2 = control_point_2

        # Calculate x, y, z polynomial coefficients. Basically we are creating
        # a cubic-spline that goes through the two control points with the
        # specified derivative at the control points.
        A = numpy.array([[0, 0, 0, 1],
                         [0, 0, 1, 0],
                         [1, 1, 1, 1],
                         [3, 2, 1, 0]])

        # If normalization is requested, then we scale the magnitude of the
        # derivative by the distance between the control points. This is
        # somewhat arbitrary, but hopefully looks reasonable to the eye.
        dv = self.cp1.location - self.cp2.location
        cp_dist = numpy.sqrt(numpy.sum(dv * dv))
        if normalize:
            scale = scale * cp_dist
            deriv1 = self.cp1.z_vec
            deriv2 = self.cp2.z_vec
        else:
            scale = 1.0
            deriv1 = self.cp1.raw_z_vec
            deriv2 = self.cp2.raw_z_vec

        vx = numpy.array([self.cp1.location[0],
                          deriv1[0]*scale,
                          self.cp2.location[0],
                          deriv2[0]*scale])

        vy = numpy.array([self.cp1.location[1],
                          deriv1[1]*scale,
                          self.cp2.location[1],
                          deriv2[1]*scale])

        vz = numpy.array([self.cp1.location[2],
                          deriv1[2]*scale,
                          self.cp2.location[2],
                          deriv2[2]*scale])

        self.x_coeff = numpy.linalg.solve(A, vx)
        self.y_coeff = numpy.linalg.solve(A, vy)
        self.z_coeff = numpy.linalg.solve(A, vz)

        # Compute distance look-up table and segment length
        table_size = 100  # Hopefully 100 sections is enough to accurately capture most curves.
        #table_size = int(round(4.0 * cp_dist))
        self.dist_lut = numpy.zeros((table_size, 2))
        self.dist_lut[0,1] = dist_offset
        total_dist = 0.0
        startp = self.xyz(0.0)
        for i in range(table_size - 1):
            p = float(i+1)/float(table_size - 1)
            endp = self.xyz(p)
            dp = endp - startp
            total_dist += numpy.sqrt(numpy.sum(dp*dp))
            self.dist_lut[i+1, 0] = p
            self.dist_lut[i+1, 1] = total_dist + dist_offset
            startp = endp
        self.length = total_dist

        # Compute perpendicular vector look-up table. We need this
        # in order to return the proper angles to go from world
        # coordinates to curve coordinates.
        self.xvec_lut = numpy.zeros((table_size, 3))
        self.xvec_lut[0,:] = self.cp1.x_vec
        for i in range(table_size - 1):
            p = float(i+1)/float(table_size - 1)
            dxyz = normVector(self.d_xyz(p))
            proj = projVector(self.xvec_lut[i,:], dxyz)
            self.xvec_lut[i+1,:] = normVector(self.xvec_lut[i,:] - proj)

        # This is so that the perpendicular vector will be propogated
        # along the curve.
        self.cp2.x_vec = self.xvec_lut[-1,:]

    #
    # This is the same approach that is used in ldraw_to_lcad.py to 
    # extract the rotation angles from the rotation matrix.
    #
    def angles(self, p, x_vec):

        # Calculate z vector.
        z_vec = normVector(self.d_xyz(p))
    
        # Calculate x vector.
        proj = projVector(x_vec, z_vec)
        x_vec = normVector(x_vec - proj)

        # Calculate y vector
        y_vec = crossProduct(z_vec, x_vec)

        # Calculate rotation angles.
        ry = math.atan2(-z_vec[0], math.sqrt(z_vec[1]*z_vec[1] + z_vec[2]*z_vec[2]))

        # If the rotation around the y axis is +- 90 then we can't separate the x-axis rotation
        # from the z-axis rotation. In this case we just assume that the x-axis rotation is
        # zero and that there was only z-axis rotation.
        if (abs(math.cos(ry)) < 1.0e-3):
            rx = 0
            rz = math.atan2(x_vec[1],y_vec[1])
        else:
            rx = math.atan2(-z_vec[1], z_vec[2])
            rz = math.atan2(-y_vec[0], x_vec[0])

        return map(lambda(x): x * 180.0/math.pi, [rx, ry, rz])

    def d_xyz(self, p):
        p_vec = numpy.array([3.0*p*p, 2.0*p, 1.0, 0.0])
        return numpy.array([numpy.sum(self.x_coeff * p_vec),
                            numpy.sum(self.y_coeff * p_vec),
                            numpy.sum(self.z_coeff * p_vec)])

    def getCoords(self, distance):

        # Extrapolate from curve start.
        if (distance <= 0):
            p = 0
            start = 0
            a_xyz = self.xyz(p) + distance * normVector(self.d_xyz(p))

        # Extrapolate from curve end.
        elif (distance >= self.length):
            p = 1
            start = len(self.dist_lut) - 2
            a_xyz = self.xyz(p) + (distance - self.length) * normVector(self.d_xyz(p))

        # Interpolate in the middle.
        else:
            # Mid-point bisection to find the bracketing 
            # points in the distance look up table.
            start = 0
            end = len(self.dist_lut) - 1
            mid = (end - start)/2
            while ((end - start) > 1):
                if (distance > self.dist_lut[mid, 1]):
                    start = mid
                elif (distance == self.dist_lut[mid, 1]):
                    start = mid
                    end = start + 1
                else:
                    end = mid
                mid = (end - start)/2 + start

            # Interpolate between bracketing points.
            ratio = (distance - self.dist_lut[start, 1])/(self.dist_lut[end, 1] - self.dist_lut[start, 1])
            p = ratio * (self.dist_lut[end, 0] - self.dist_lut[start, 0]) + self.dist_lut[start, 0]
        
            # Get xyz
            a_xyz = self.xyz(p)

        # Get angles
        [rx, ry, rz] = self.angles(p, self.xvec_lut[start,:])
        return [a_xyz[0], a_xyz[1], a_xyz[2], rx, ry, rz]

    def xyz(self, p):
        p_vec = numpy.array([p*p*p, p*p, p, 1.0])
        return numpy.array([numpy.sum(self.x_coeff * p_vec),
                            numpy.sum(self.y_coeff * p_vec),
                            numpy.sum(self.z_coeff * p_vec)])


#
# Testing
#
if (__name__ == "__main__"):

    cp1 = ControlPoint(0, 0, 0, 1.0, 1.0, 0, 0, 0, 1.0)
    cp2 = ControlPoint(5, 0, 0, 1.0, 0, 0)
    cp3 = ControlPoint(10, 0, 0, 1.0, 1.0, 0)

    curve = Curve(True, 1.0, 0)
    curve.addSegment(cp1, cp2)
    curve.addSegment(cp2, cp3)
    
    print curve.getCoords(1)
    exit()

    print curve.length

    x = numpy.arange(0.0, curve.length, 0.4)
    xf = numpy.zeros(x.size)
    yf = numpy.zeros(x.size)
    for i in range(x.size):
        [cx, cy, cz, rx, ry, rz] = curve.getCoords(x[i])
        print rx, ry, rz
        xf[i] = cx
        yf[i] = cy

    import matplotlib.pyplot as plt
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1, aspect = 1.0)
    #ax = fig.add_subplot(1,1,1)
    ax.scatter(xf, yf)
    plt.show()


#
# The MIT License
#
# Copyright (c) 2015 Hazen Babcock
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
