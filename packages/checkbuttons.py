
from collections import OrderedDict
from numpy import array

try:
    import tkinter

except ImportError:
    import Tkinter as tkinter

class CheckButton:
    """
    Class for GUI filtering of input chkbutton_dict.
    """

    def __init__(self,
                 master, chkbuttons_dict):

        self.master = master
        self.chkbuttons = sorted(chkbuttons_dict.items(),
                                 key=lambda x: x[1])

        self.start = 0
        self.checkbuttons = []
        self.vars = []

        self.scrollbar = tkinter.Scrollbar(orient='vertical')
        self.text = tkinter.Text(self.master, width=40, height=15,
                                 yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.text.yview)
        self.scrollbar.pack(side='right', fill='y')
        self.text.pack(side='top', fill='both', expand=True)

        for i, chkbutton in enumerate(self.chkbuttons):

            self.vars.append(tkinter.IntVar(value=1))
            self.checkbuttons.append(tkinter.Checkbutton(text=chkbutton[1],
                                                         variable=self.vars[i],
                                                         padx=0, pady=0, bd=0))

        for checkbutton in self.checkbuttons:

            self.text.window_create('end', window=checkbutton)
            self.text.insert('end', '\n')
            checkbutton.bind('<Button-1>', self._selectstart)
            checkbutton.bind('<Shift-Button-1>', self._selectrange)

    def _selectstart(self, event):
        """
        Selects checkbutton.
        This function call is bound to <Button-1> key.

        Args:
            self: the instance of the class;
            event: the event object.
        """

        self.start = self.checkbuttons.index(event.widget)

    def _selectrange(self, event):
        """
        Selects multiple checkbuttons.
        This function call is bound to <Shift-Button-1> key.

        Args:
            self: the instance of the class;
            event: the event object.
        """

        start = self.start
        end = self.checkbuttons.index(event.widget)
        indices = slice(min(start, end) + 1, max(start, end))

        for chkbutton in self.checkbuttons[indices]:
            chkbutton.toggle()

        self.start = end

    @property
    def selection(self):
        """
        Return:
            dict: dictionary with selected checkbuttons.
        """

        ids = [i for i, var in enumerate(self.vars) if var.get()]

        return OrderedDict(array(self.chkbuttons)[ids]) if ids else {}

def test(checkbuttons,
         title='', comment=''):
    """
    """

    root = tkinter.Tk()
    root.focus_force()
    root.title(title)

    window_width = root.winfo_reqwidth()
    window_height = root.winfo_reqheight()
    pos_right = int(root.winfo_screenwidth()/2 - window_width/2)
    pos_down = int(root.winfo_screenheight()/2 - window_height/2)
    root.geometry(f'+{pos_right}+{pos_down}')

    # Add label widget to root widget.
    if comment:
        label = tkinter.Label(root, text=comment)
        label.pack(side='top', fill='both')

    chkbuttons = CheckButton(root, checkbuttons)

    # Add button widget to root widget.
    button = tkinter.Button(root, text='OK',
                            command=root.destroy)
    button.pack(side='top', fill='both')
    root.mainloop()

    return chkbuttons.selection

if __name__ == '__main__':
    CHKBUTTONS = {
        1: u'ISSUE1',
        2: u'ISSUE2',
        3: u'ISSUE3',
        4: u'ISSUE4',
        5: u'ISSUE5'}
    test(CHKBUTTONS, 'Checkbuttons')
