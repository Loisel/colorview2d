import sys
from colorview2d import Colorview2d

def main(args=None):
    if args is None:
        args = sys.argv[1:]

    app = Colorview2d()
    app.MainLoop()

if __name__ == "__main__":
    main()