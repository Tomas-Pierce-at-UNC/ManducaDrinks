
import math
import numpy

class Point:

    SQRT_2 = math.sqrt(2)

    __slots__ = ["x", "y"]

    def __init__(self,x,y):

        self.x = x

        self.y = y

    def distance(self, other):
        delta_x = self.x - other.x
        delta_y = self.y - other.y
        discriminant = (delta_x ** 2) + (delta_y ** 2)
        return math.sqrt(discriminant)

    def get(self, image :numpy.ndarray):
        return image[self.y,self.x]

    def __str__(self):
        return f"Point({self.x},{self.y})"

    def __repr__(self):
        return f"Point({self.x},{self.y})"

    def four_connected(self, other):
        return self.distance(other) == 1

    def eight_connected(self,other):
        distance = self.distance(other)
        return 1 <= distance <= self.SQRT_2
        
