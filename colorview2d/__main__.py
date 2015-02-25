import sys
import logging
from optparse import OptionParser

from pydispatch import dispatcher
import utils
from mainframe import MainFrame
import wx


"""
colorview2d
~~~~~~~~~~~

A GUI driven application to visualize and analyze 3D
datasets. Available tools include linear slope extraction,
linecut series extraction and a linetrace viewer.

:copyright: 2014 by Alois Dirnaichner, see AUTHORS for more details
:license: GPLv3, see LICENSE for more details
"""



class Colorview2d(wx.App):
    """
    The colorview2d application object.
    It is used to parse the configuration
    and create the first View object.
    """
    
    def __init__(self, redirect = False, cv2dpath = None, filename = None, datafilename = None, columns = None):
        self.datafilename = datafilename
        self.columns = columns
        self.cv2dpath = cv2dpath
        dispatcher.connect(self.handle_print_events)
        wx.App.__init__(self, redirect, filename)

    def handle_print_events(self,sender,signal):
        logging.debug('{} sent signal: {}'.format(sender,signal))
        
    def OnInit(self):
        # create frame here
        self.frame = MainFrame(self,self.cv2dpath,self.datafilename,self.columns)
        self.frame.Show()
        self.SetTopWindow(self.frame)
        self.frame.Layout()
        return True



def main(args=None):

    if args is None:
        args = sys.argv[1:]

    parser = OptionParser()
    parser.add_option("--log", dest="loglevel", default='WARN',
                help="Specify log level")

    parser.add_option("-f","--file", dest="filename", default=None, type="string",
                      help="Specify a file name to open.")
    parser.add_option("--columns", dest="columns", default=None, type="string",
                      help="Specify the columns of a file to open.\n\
                      The syntax is a,b,c with a,b and c being integers in the range 0-9")
    parser.add_option("-c","--cv2d", dest="cv2dpath", default=None, type="string",
                      help="Specify a config file name to open.")

    (options, args) = parser.parse_args()

    logging.basicConfig(level=getattr(logging,options.loglevel.upper()))

    if options.cv2dpath:
        logging.info("Loading config file {}".format(options.cv2dpath))
        options.filename = None
        options.columns = None
    
    if options.columns and not options.filename:
        print "Option -c or --columns requires option -f or --file."
        parser.print_help()
        exit(-1)

        logging.info("Using columns {} for plotting file {}.".format(options.columns,options.filename))

    app = Colorview2d(cv2dpath=options.cv2dpath,datafilename=options.filename,columns=options.columns)
    app.MainLoop()

if __name__ == "__main__":
    main()
