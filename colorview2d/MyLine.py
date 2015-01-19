import numpy as np

class MyLine():
    """
    Represents a line drawn in a matplotlib axes object.

    This is a utility class that provides mainly slope and shift of the line.
    Lines can also be labeled in the plot.

    Attributes:
      x1,x2,y1,y2 (float): Two points defining the line.
      comment (string): A string describing the line.
      axes (matplotlib axes): Axes object to create the line in.
      line (matplotlib line): The lineplot associated with the axes object.
      commenttext (matplotlib text): The commenttext plotted in the axes object.
    """
    def __init__(self,axes,x1 = 0, x2 = 0, y1 = 0, y2 = 0, comment=""):
        self.x1 = x1
        self.y1 = y1
        self.y2 = y2
        self.x2 = x2
        self.comment = comment

        self.axes = axes
        self.line, = self.axes.plot([self.x1,self.x2],[self.y1,self.y2])
        self.commenttext = self.axes.text(self.x1,self.y1-0.5,self.comment)

        self.dx = self.x2-self.x1
        self.dy = self.y2-self.y1

    def addline(self,axes):
        self.axes = axes
        self.commenttext = self.axes.text(self.x1,self.y1-0.5,self.comment)
        self.line, = self.axes.plot([self.x1,self.x2],[self.y1,self.y2])

    def removeline(self):
        self.commenttext.remove()
        self.line.remove()

    def set_data(self,x1,x2,y1,y2):
        self.x1 = x1
        self.y1 = y1
        self.y2 = y2
        self.x2 = x2

        self.dx = self.x2-self.x1
        self.dy = self.y2-self.y1

        self.line.set_data([x1,x2],[y1,y2])

    def set_comment(self,comment):
        self.comment = comment
        self.commenttext.remove()
        self.commenttext = self.axes.text(self.x1,self.y1-0.5,self.comment)


    def get_slope(self):        
        try:
            return self.dy/self.dx
        except ZeroDivisionError:
            print "Slope not defined for a perpendicular line."
        
    def get_shift(self):
        return self.y1-self.get_slope()*self.x1
            
    def get_y(self,x):
        return x*self.get_slope()+self.get_shift()

    def get_x(self,y):
        return (y-self.get_shift())/self.get_slope()

    def get_comment(self):
        return self.comment
