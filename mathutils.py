# brief         part of ax-breakout game
# author        Wojciech Szęszoł keepitsimplesirius[at]gmail.com
# encoding      UTF-8 with BOM
# end of line   LF
# tab           4x space

from math import *

class vec2:
    def __init__(self, x = 0.0, y = 0.0):
        self.x = x
        self.y = y

    def __add__(a, b):
        return vec2(a.x + b.x, a.y + b.y)

    def __sub__(a, b):
        return vec2(a.x - b.x, a.y - b.y)

    def __mul__(a, b):
        if isinstance(b, vec2):
            return vec2(a.x * b.x, a.y * b.y)
        else:
            return vec2(a.x * b, a.y * b)

    def __truediv__(a, b):
        if isinstance(b, vec2):
            return vec2(a.x / b.x, a.y / b.y)
        else:
            return vec2(a.x / b, a.y / b)

    def __rootdiv__(a, b):
        if isinstance(b, vec2):
            return vec2(a.x // b.x, a.y // b.y)
        else:
            return vec2(a.x // b, a.y // b)

    def __pos__(a):
        return vec2(+a.x, +a.y)

    def __neg__(a):
        return vec2(-a.x, -a.y)

    def __eq__(a, b):
        return a.x == b.x and a.y == b.y

    def __ne__(a, b):
        return a.x != b.x or a.y != b.y

    def __setitem__(self, index, value):
        if index == 0:
            self.x = value
        else:
            self.y = value

    def __getitem__(self, index):
        if index == 0:
            return self.x
        else:
            return self.y

    def __str__(self):
        return "[" + str(self.x) + ", " + str(self.y) + "]"

    def __repr__(self):
        return "[" + str(self.x) + ", " + str(self.y) + "]"

    def couple(self):
        return self.x, self.y

    def lengthsq(self):
        return self.x * self.x + self.y * self.y

    def length(self):
        return sqrt(self.x * self.x + self.y * self.y)

    def normal(self):
        inv = 1.0 / self.length()
        return vec2(self.x * inv, self.y * inv)

    def intcpl(self):
        return int(self.x), int(self.y)

    def abs(self):
        return vec2(abs(self.x), abs(self.y))

def toVec2(couple):
    return vec2(couple[0], couple[1])

def rotate2(vector, angle):
    s = sin(angle)
    c = cos(angle)
    x = c * vector.x - s * vector.y
    y = s * vector.x + c * vector.y
    return vec2(x, y)

def reflect2(vector, normal):
    proj = normal * dot2(vector, normal)
    return -vector + proj * 2

def dot2(vec_a, vec_b):
    return vec_a.x * vec_b.x + vec_a.y * vec_b.y

def rectInsideRect(first_position, first_size, second_position, second_size):
    distance = (first_position - second_position).abs() + first_size
    return distance.x < second_size.x and distance.y < second_size.y

def rectRectIntersect(first_position, first_size, second_position, second_size):
    """Tests only if given rectangles intersect, returns True or False"""
    distance = (first_position - second_position).abs()
    limit = first_size + second_size
    return distance.x < limit.x and distance.y < limit.y

def lineSegmentIntersect(line_point, line_tangent, segment_begin, segment_end):
    kx = segment_end.x - segment_begin.x
    ky = segment_end.y - segment_begin.y
    n = line_point.y * line_tangent.x - line_point.x * line_tangent.y - segment_begin.y * line_tangent.x + segment_begin.x * line_tangent.y
    d = ky * line_tangent.x - kx * line_tangent.y
    if d == 0.0:
        if n == 0.0:
            return segment_begin
        else:
            return False
    else:
        r = n / d
        if r < 0.0 or r > 1.0:
            return False
        else:
            x = segment_begin.x + r * kx
            y = segment_begin.y + r * ky
            return vec2(x, y)

def circleSectorCollide(circle_position, circle_radius, sector_position, sector_radius, sector_angle):
    distance = (circle_position - sector_position).lengthsq()
    radiussq = circle_radius + sector_radius
    radiussq *= radiussq
    if distance < radiussq:
        normal = (circle_position - sector_position).normal()
        c = dot2(vec2(0.0, -1.0), normal)
        c = acos(c)
        if c < sector_angle:
            return sector_position + normal * sector_radius, normal
        else:
            return False
    else:
        return False

def circleCircleCollide(first_position, first_radius, second_position, second_radius):
    normal = first_position - second_position
    distance = normal.lengthsq()
    radiussq = (first_radius + second_radius)
    radiussq *= radiussq
    if distance < radiussq:
        normal = normal.normal()
        point = second_position + normal * second_radius
        return point, normal
    else:
        return False

def circleRectangleCollide(circle_position, circle_radius, rectangle_position, rectangle_size):
    """Rectangle size is actually halfed size (vec2(w/2, h/2))."""
    distance = (circle_position - rectangle_position).abs()
    dist_lim = vec2(circle_radius + rectangle_size.x, circle_radius + rectangle_size.y)
    if distance.x < dist_lim.x and distance.y < dist_lim.y:
        if distance.x < rectangle_size.x:
            normal = vec2(0, circle_position.y - rectangle_position.y).normal()
            point = vec2(circle_position.x, rectangle_position.y + normal.y * rectangle_size.y)
            return point, normal
        elif distance.y < rectangle_size.y:
            normal = vec2(circle_position.x - rectangle_position.x, 0).normal()
            point = vec2(rectangle_position.x + normal.x * rectangle_size.x, circle_position.y)
            return point, normal
        else:
            radiussq = circle_radius * circle_radius
            point = vec2(rectangle_position.x - rectangle_size.x, rectangle_position.y - rectangle_size.y)
            distance = (circle_position - point).lengthsq()
            if distance < radiussq:
                normal = (circle_position - point).normal()
                return point, normal

            radiussq = circle_radius * circle_radius
            point = vec2(rectangle_position.x + rectangle_size.x, rectangle_position.y - rectangle_size.y)
            distance = (circle_position - point).lengthsq()
            if distance < radiussq:
                normal = (circle_position - point).normal()
                return point, normal

            radiussq = circle_radius * circle_radius
            point = vec2(rectangle_position.x - rectangle_size.x, rectangle_position.y + rectangle_size.y)
            distance = (circle_position - point).lengthsq()
            if distance < radiussq:
                normal = (circle_position - point).normal()
                return point, normal

            radiussq = circle_radius * circle_radius
            point = vec2(rectangle_position.x + rectangle_size.x, rectangle_position.y + rectangle_size.y)
            distance = (circle_position - point).lengthsq()
            if distance < radiussq:
                normal = (circle_position - point).normal()
                return point, normal

            return False
    else:
        return False

def circleInsideCollision(circle_position, circle_radius, inside_position, inside_size):
    """Checks collision between the circle and containing it rectangle."""
    distance = (inside_position - circle_position).abs() + vec2(circle_radius, circle_radius)
    if distance.x > inside_size.x and distance.y > inside_size.y:
        normal = (inside_position - circle_position).normal()
        point = circle_position - normal * circle_radius
        return point, normal
    elif distance.x > inside_size.x:
        normal = vec2(inside_position.x - circle_position.x, 0).normal()
        point = vec2(-normal.x * inside_size.x + inside_position.x, circle_position.y)
        return point, normal
    elif distance.y > inside_size.y:
        normal = vec2(0, inside_position.y - circle_position.y).normal()
        point = vec2(circle_position.x, -normal.y * inside_size.y + inside_position.y)
        return point, normal
    else:
        return False