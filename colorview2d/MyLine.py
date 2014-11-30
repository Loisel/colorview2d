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
    def __init__(self,axes,x1 = 0, y1 = 0, x2 = 0, y2 = 0, comment=""):
        self.x1 = x1
        self.y1 = y1
        self.y2 = y2
        self.x2 = x2
        self.comment = comment

        self.axes = axes
        self.line, = self.axes.plot([self.x1,self.x2],[self.y1,self.y2])
        self.commenttext = self.axes.text(self.x1,self.y1-0.5,self.comment)



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


    def get_y(self,x):
        return (x-self.x1)/self.dx

    def get_x(self,y):
        return (y-self.y1)/self.dy

    def get_comment(self):
        return self.comment
