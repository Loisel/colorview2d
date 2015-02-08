import sys
import logging
from optparse import OptionParser

from colorview2d import Colorview2d
import Utils

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
