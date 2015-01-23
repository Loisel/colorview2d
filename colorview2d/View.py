from Subject import Subject
import yaml

class View(Subject):
    def __init__(self,datafile,modlist=[]):
        Subject.__init__(self)
        self.modlist = list(modlist)
        self.set_datafile(datafile)

    def dump_list(self):
        return yaml.dump_all(self.modlist, explicit_start=True)

    def set_list(self,modlist):
        self.modlist = modlist
        self.apply()
    
    def addMod(self,mod):
        """
        Adds a modification object to the list

        Args:
          mod (modification): Modification object to add.
        """

        for mymod in self.modlist:
            if mymod.title() == mod.title():
                self.modlist.remove(mod)
        
        self.modlist.append(mod)

        self.apply()


    def remMod(self,title):
        """
        Removes a modification object from the list using a string identifier.

        Args:
          title (string): string specifying the modification
        """
        
        for mod in self.modlist:
            if mod.title() == title:
                self.modlist.remove(mod)

        self.apply()

    def hasMod(self,title):
        """
        Checks if the modlist contains a mod using a string identifier.

        Args:
          title (string): string specifying the modification
        """
        for mod in self.modlist:
            if mod.title() == title:
                return True

        return False


    def apply(self):
        """
        Applies the modlist to the datafile in the parent frame.
        
        The datafile is first reverted to its original state,
        then mods are applied in the order they were added.
        Observers are notifed.
        """

        self.datafile = self.original_datafile.deep_copy()

        for mod in self.modlist:
#            print "Applying mod {}".format(mod.title())
            mod.apply_mod(self.datafile)
        
        self.notify()

    def reset(self):
        """
        Resets the datafile object by emptying the modlist.
        """

        self.modlist = []
        self.apply()
        
    def get_data(self):
        """
        Shortcut for the 2d data contained int the datafile. 
        Interface for plotting routine.
        """
        return self.datafile.Zdata

    def set_datafile(self,datafile):
        """
        Sets the datafile.
        The original datafile is replaced as well and the modlist is applied.

        Args:
          datafile: a datafile object
        """
        self.datafile = datafile
        self.original_datafile = datafile.deep_copy()
        self.apply()

    def rotate_cw(self):
        """
        Resets the datafile and rotates it clockwise.
        """

        # datafile.rotate returns a rotated version of self.
        # That is why set_datafile is used.

        self.reset()
        self.set_datafile(self.datafile.rotate_cw())

    def rotate_ccw(self):
        """
        Resets the datafile and rotates it anti-clockwise.
        """

        # datafile.rotate returns a rotated version of self.
        # That is why set_datafile is used.

        self.reset()
        self.set_datafile(self.datafile.rotate_ccw())
