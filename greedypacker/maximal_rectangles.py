#!/usr/bin/env python
"""
Maximal Rectangle 2D Bin Algorithm

Solomon Bothwell
ssbothwell@gmail.com
"""
import operator
import typing
from typing import List, Tuple, Union
from functools import reduce
from collections import namedtuple
from .item import Item


class FreeRectangle(typing.NamedTuple('FreeRectangle', [('width', int), ('height', int), ('x', int), ('y', int)])):
    __slots__ = ()
    @property
    def area(self):
        return self.width*self.height


class MaximalRectangle:
    def __init__(self, x: int = 8,
                 y: int = 4,
                 rotation: bool = True,
                 rectangle_merge: bool=False,
                 split_heuristic: str='default') -> None:
        self.x = x
        self.y = y
        self.rMerge = rectangle_merge
        self.split_heuristic = split_heuristic


        if x == 0 or y == 0:
            self.freerects = [] # type: List[FreeRectangle]
        else:
            self.freerects = [FreeRectangle(self.x, self.y, 0, 0)] # type: List[FreeRectangle]
        self.items = [] # type: List[Item]
        self.rotation = rotation


    def __repr__(self) -> str:
        return "MaximalRectangle(%r)" % (self.items)


    @staticmethod
    def item_fits_rect(item: Item,
                       rect: FreeRectangle,
                       rotation: bool=False) -> bool:
        if (item.width <= rect.width and item.height <= rect.height):
            return True
        if (rotation and 
            item.height <= rect.width and 
            item.width <= rect.height):
            return True
        return False


    @staticmethod
    def split_rectangle(rectangle: FreeRectangle,
                        item: Item) -> List[FreeRectangle]:
        """
        Return a list of maximal free rectangles from a split
        """
        results = []
        if item.width < rectangle.width:
            Fw = rectangle.width - item.width
            Fh = rectangle.height
            Fx = rectangle.x + item.width
            Fy = rectangle.y
            results.append(FreeRectangle(width=Fw,
                                         height=Fh,
                                         x=Fx,
                                         y=Fy))
        if item.height < rectangle.height:
            Fw = rectangle.width
            Fh = rectangle.height - item.height
            Fx = rectangle.x 
            Fy = rectangle.y + item.height
            results.append(FreeRectangle(width=Fw,
                                         height=Fh,
                                         x=Fx,
                                         y=Fy))
        return results
    

    @staticmethod
    def item_bounds(item: Item) -> tuple:
        """
        Returns the lower left and upper right 
        corners of the item's bounding box.
        """
        return (item.CornerPoint[0], item.CornerPoint[1], item.CornerPoint[0]+item.width, item.CornerPoint[1]+item.height)


    @staticmethod
    def checkInstersection(free_rect: FreeRectangle,
                           bounding_box: tuple) -> bool:
        """ 
        Checks if bounding box intersects rectangle
        """

        # Check if nodes actually intersect
        if (bounding_box[0] >= free_rect.x + free_rect.width or
            bounding_box[2] <= free_rect.x or
            bounding_box[1] >= free_rect.y + free_rect.height or
            bounding_box[3] <= free_rect.y):
            return False
        return True
        

    @staticmethod
    def findOverlap(F1: FreeRectangle, B: tuple ) -> tuple:
        """
        returns the bottom left and top right 
        coordinates of the overlap
        """
        X1, Y1 = F1.x, F1.y
        X2, Y2 = F1.x+F1.width, F1.y+F1.height
        X3, Y3 = B[0], B[1]
        X4, Y4 = B[2], B[3]

        X5 = max(X1, X3)
        Y5 = max(Y1, Y3)
        X6 = min(X2, X4)
        Y6 = min(Y2, Y4)

        return (X5, Y5, X6, Y6)

    @staticmethod
    def clipOverlap(rect: FreeRectangle,
                         overlap: tuple) -> List[FreeRectangle]:
        """
        Return maximal rectangles for  non-intersected 
        parts of rect.
        """
        Fx, Fy = rect.x, rect.y
        Fw, Fh = rect.width, rect.height
        Ox1, Oy1, Ox2, Oy2 = overlap
                
        results = []
        
        ## Check for non-intersected sections
        # Left Side
        if Ox1 > Fx:
            L = FreeRectangle(width=Ox1-Fx, height=Fh, x=Fx, y=Fy)
            results.append(L)
        # Right side
        if Ox2 < Fx + Fw:
            R = FreeRectangle(width=(Fx+Fw)-Ox2, height=Fh, x=Ox2, y=Fy)
            results.append(R)
        # Bottom Side
        if Oy1 > Fy:
            B = FreeRectangle(width=Fw, height=Oy1-Fy, x=Fx, y=Fy)
            results.append(B)
        # Top Side
        if Oy2 < Fy + Fh:
            T = FreeRectangle(width=Fw, height=(Fy+Fh)-Oy2, x=Fx, y=Oy2)
            results.append(T)

        return results
       
        
    @staticmethod
    def encapsulates(F0: FreeRectangle,
                     F1: FreeRectangle) -> bool:
        """
        Returns true if F1 is fully encapsulated
        inside F0
        """
        if F1.x < F0.x or F1.x > F0.x+F0.width:
            return False
        if F1.x+F1.width > F0.x+F0.width:
            return False
        if F1.y < F0.y or F1.y > F0.y+F0.height:
            return False
        if F1.y+F1.height > F0.y+F0.height:
            return False
        return True


    def remove_redundent(self) -> List[FreeRectangle]:
        """
        Remove all FreeRectangle full encapsulated
        inside another FreeRectangle.
        """
        i = 0
        while i < len(self.freerects):
            j = i + 1
            while j < len(self.freerects):
                if self.encapsulates(self.freerects[j], self.freerects[i]):
                    del self.freerects[i]
                    i -= 1
                    break
                if self.encapsulates(self.freerects[i], self.freerects[j]):
                    del self.freerects[j]
                    j -= 1
                j += 1
            i += 1
        return self.freerects


    def prune_overlaps(self, itemBounds: tuple) -> None:
        """
        Loop through all FreeRectangles and prune
        any overlapping the itemBounds
        """
        result = []
        for rect in self.freerects:
            if self.checkInstersection(rect, itemBounds):
                overlap = self.findOverlap(rect, itemBounds)
                new_rects = self.clipOverlap(rect, overlap)
                result += new_rects
            else:
                result.append(rect)
        self.freerects = result
        self.remove_redundent()


    def first_fit(self, item: Item) -> bool:
        """
        Select first indexed FreeRectangle (that fits item)
        """
        
        for el in self.freerects:
            if self.item_fits_rect(item, el):
                item.CornerPoint = el.x, el.y
                self.items.append(item)
                maximals = self.split_rectangle(el, item)
                self.freerects.remove(el)
                self.freerects += maximals
                itemBounds = self.item_bounds(item)

                self.prune_overlaps(itemBounds)
                return True
        return False


    def best_area(self, item: Item) -> bool:
        """
        Insert item into rectangle with smallest
        area
        """
        best_rect = None
        best_area = float('inf')
        for rect in self.freerects:
            if not self.item_fits_rect(item, rect):
                continue
            area = rect.width*rect.height 
            if area < best_area:
                best_rect = rect
                best_area = area
        if best_rect:
            item.CornerPoint = best_rect.x, best_rect.y
            self.items.append(item)
            maximals = self.split_rectangle(best_rect, item)
            self.freerects.remove(best_rect)
            self.freerects += maximals
            itemBounds = self.item_bounds(item)

            self.prune_overlaps(itemBounds)
            return True
        return False


    def best_shortside(self, item: Item) -> bool:
        """
        Pack Item into a FreeRectangle such that
        the smaller leftover side is minimized, ie:
        pick the FreeRectangle where min(Fw - Iw, Fh - Ih)
        is the smallest.
        """
        best_rect = None
        best_shortside = float('inf')
        for rect in self.freerects:
            if not self.item_fits_rect(item, rect):
                continue
            shortside = min(rect.width-item.width,
                            rect.height-item.height)
            if shortside < best_shortside:
                best_rect = rect
                best_shortside = shortside
        if best_rect:
            item.CornerPoint = best_rect.x, best_rect.y
            self.items.append(item)
            maximals = self.split_rectangle(best_rect, item)
            self.freerects.remove(best_rect)
            self.freerects += maximals
            itemBounds = self.item_bounds(item)

            self.prune_overlaps(itemBounds)
            return True
        return False


    def best_longside(self, item: Item) -> bool:
        """
        Pack Item into a FreeRectangle such that
        the larger leftover side is minimized, ie:
        pick the FreeRectangle where max(Fw - Iw, Fh - Ih)
        is the smallest.
        """
        best_rect = None
        best_longside = float('inf')
        for rect in self.freerects:
            if not self.item_fits_rect(item, rect):
                continue
            longside = max(rect.width-item.width,
                           rect.height-item.height)
            if longside < best_longside:
                best_rect = rect
                best_longside = longside
        if best_rect:
            item.CornerPoint = best_rect.x, best_rect.y
            self.items.append(item)
            maximals = self.split_rectangle(best_rect, item)
            self.freerects.remove(best_rect)
            self.freerects += maximals
            itemBounds = self.item_bounds(item)

            self.prune_overlaps(itemBounds)
            return True
        return False


    def best_bottomleft(self, item: Item) -> bool:
        """
        Pack Item into a FreeRectangle such that
        the item's top coordinate will be minimized. 
        If multiple FreeRectangles result in minimal 
        top heights, then choose then one with the 
        smallest x
        """
        best_rect = None
        best_topy = float('inf')
        for rect in self.freerects:
            if not self.item_fits_rect(item, rect):
                continue
            topy = item.height + rect.y  
            if ((topy == best_topy and rect.x < best_rect.x) or
                 topy < best_topy):
                best_rect = rect
                best_topy = topy

        if best_rect:
            item.CornerPoint = best_rect.x, best_rect.y
            self.items.append(item)
            maximals = self.split_rectangle(best_rect, item)
            self.freerects.remove(best_rect)
            self.freerects += maximals
            itemBounds = self.item_bounds(item)

            self.prune_overlaps(itemBounds)
            return True
        return False

    
    @staticmethod
    def common_interval_length(Xstart: int, Xend: int,
                               Ystart: int, Yend: int) -> int:
        """
        Returns the length of perimiter shared by two
        rectangles
        """
        if Xend < Ystart or Yend < Xstart:
            return 0
        return min(Xend, Yend) - max(Xstart, Ystart)

    
    def contact_point(self, item: Item) -> bool:
        """
        Pack Item into a FreeRectangle such that
        the permiter of Item that is touching either
        the bin edge or another packed item is
        maximized.
        """
        best_rect = None
        best_perim = -1
        for rect in self.freerects:
            if not self.item_fits_rect(item, rect):
                continue

            perim = 0
            if rect.x == 0 or rect.x + item.width == self.x:
                perim += item.height
            if rect.y == 0 or rect.y + item.height == self.y:
                perim += item.width

            for itm in self.items:
                if (itm.x == rect.x+rect.width or
                    itm.x+itm.width == rect.x):
                    perim += self.common_interval_length(itm.y, itm.y+itm.height, rect.y, rect.y+item.height)
                if (itm.y == rect.y+rect.height or
                    item.y+itm.height == rect.y):
                    perim += self.common_interval_length(itm.x, itm.x+itm.width, rect.x, rect.x+item.width)
            if perim > best_perim:
                best_rect = rect
                best_perim = perim

        if best_rect:
            item.CornerPoint = best_rect.x, best_rect.y
            self.items.append(item)
            maximals = self.split_rectangle(best_rect, item)
            self.freerects.remove(best_rect)
            self.freerects += maximals
            itemBounds = self.item_bounds(item)

            self.prune_overlaps(itemBounds)
            return True
        return False