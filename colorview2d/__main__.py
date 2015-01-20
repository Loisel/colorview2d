import sys
import logging
from optparse import OptionParser

from colorview2d import Colorview2d

def main(args=None):
    if args is None:
        args = sys.argv[1:]

    parser = OptionParser()
    parser.add_option("--log", dest="loglevel",
                  help="Specify log level")
    

    (options, args) = parser.parse_args()
    
    logging.basicConfig(level=getattr(logging,options.loglevel.upper()))
    app = Colorview2d()
    app.MainLoop()

if __name__ == "__main__":
    main()