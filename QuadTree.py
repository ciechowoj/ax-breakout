# brief         part of ax-breakout game
# author        Wojciech Szęszoł keepitsimplesirius[at]gmail.com
# encoding      UTF-8 with BOM
# end of line   LF
# tab           4x space

from mathutils import *

class QuadTree:
    def __init__(self, position, size, depth):
        self.depth = depth
        self.size = size
        self.position = position
        if depth != 0:
            child_size = size * 0.5
            child_depth = depth - 1
            p0 = vec2(position.x + child_size.x, position.y + child_size.y)
            p1 = vec2(position.x - child_size.x, position.y + child_size.y)
            p2 = vec2(position.x + child_size.x, position.y - child_size.y)
            p3 = vec2(position.x - child_size.x, position.y - child_size.y)
            self.children = (QuadTree(p0, child_size, child_depth), QuadTree(p1, child_size, child_depth), QuadTree(p2, child_size, child_depth), QuadTree(p3, child_size, child_depth))
        else:
            self.children = []
        self.elements = []

    def insert(self, element):
        if self.depth != 0:
            for x in self.children:
                if rectRectIntersect(element.position, element.size, x.position, x.size):
                    x.insert(element)
        else:
            self.elements.append(element)

    def remove(self, element):
        if self.depth != 0:
            for x in self.children:
                if rectRectIntersect(element.position, element.size, x.position, x.size):
                    x.remove(element)
        else:
            i = 0; s = len(self.elements)
            while i < s:
                if self.elements[i] == element:
                    del self.elements[i]
                    i -= 1
                    s -= 1
                i += 1
                
    def collide(self, element):
        if self.depth != 0:
            result = []
            for x in self.children:
                if rectRectIntersect(x.position, x.size, element.position, element.size):
                    result += x.collide(element)
            return result
        else:
            return self.elements

    def __repr__(self):
        return str(len(self.elements))
