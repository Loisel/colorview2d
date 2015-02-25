import wx

class FloatValidator(wx.PyValidator):
    """ This validator is used to ensure that the user has entered something
        into the text object editor dialog's text field.
    """
    def __init__(self,default):
        """ Standard constructor.
        """
        wx.PyValidator.__init__(self)
        self.default = default



    def Clone(self):
        """ Standard cloner.

            Note that every validator must implement the Clone() method.
        """
        return FloatValidator(self.default)

    def Validate(self, win):
        textCtrl = self.GetWindow()
        num_string = textCtrl.GetValue()
        try:
            float(num_string)
        except:
            textCtrl.SetValue(self.default)
            return False
        return True


    def TransferToWindow(self):
        """ Transfer data from validator to window.

            The default implementation returns False, indicating that an error
            occurred.  We simply return True, as we don't do any data transfer.
        """
        return True # Prevent wxDialog from complaining.


    def TransferFromWindow(self):
        """ Transfer data from window to validator.

            The default implementation returns False, indicating that an error
            occurred.  We simply return True, as we don't do any data transfer.
        """
        return True # Prevent wxDialog from complaining.
