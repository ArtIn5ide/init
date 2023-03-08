import sys
import gc
import calendar
import subprocess
from pathlib import Path

try:
    import tkinter
    from tkinter import messagebox

except ImportError:
    import Tkinter as tkinter
    import tkMessageBox as messagebox

sys.path.append(str(Path(__file__).parent))

from ttkcalendar import Calendar
from checkbuttons import CheckButton
from constants import DESCRIPTION

def checkbuttons_window(checkbuttons,
                        title='', comment=''):
    """
    Creates GUI window with CheckButton widget (from checkbuttons.py).
    Function returns selected checkbuttons by the user from input checkbuttons.

    Args:
        checkbuttons (dict): input dict with (chkbutton_iid, chkbutton_name);
        title (str, default=''): root widget title;
        comment (str, default=''): comment to root widget;

    Return:
        chkbuttons.selection (dict): selected by the user checkbuttons
                                     from input checkbuttons.
    """

    # Create root widget and set title and geometry.
    root = tkinter.Tk()
    root.focus_force()
    root.title(title)

    window_width = root.winfo_reqwidth()
    window_height = root.winfo_reqheight()
    pos_right = int(root.winfo_screenwidth()/2 - window_width/2)
    pos_down = int(root.winfo_screenheight()/2 - window_height)
    root.geometry(f'+{pos_right}+{pos_down}')

    # Add label widget to root widget.
    if comment:
        label = tkinter.Label(root, text=comment)
        label.pack(side='top', fill='both')

    # Add CheckButton widget (from checkbuttons.py) to root.
    chkbuttons = CheckButton(root, checkbuttons)

    # Add button widget to root widget.
    button = tkinter.Button(root, text='OK',
                            command=root.destroy)
    button.pack(side='top', fill='both')

    # 'root' window (widget) close event handler.
    root.protocol('WM_DELETE_WINDOW',
                  lambda arg=root: on_closing(arg))
    root.mainloop()
    gc.collect()
    return chkbuttons.selection

def calendar_window(title='',
                    comment=''):
    """
    Creates GUI window with calendar widget (from ttkcalendar.py).
    Function returns selected date by the user.

    Args:
        title (str, default=''): root widget title;
        comment (str, default=''): comment to root widget;

    Return:
        ttkcal.selection (datetime obj): selected date from GUI calendar.
    """

    # Create root widget and set title and geometry.
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

    # Add ttkcalendar widget (from ttkcalendar.py) to root.
    ttkcal = Calendar(firstweekday=calendar.MONDAY)
    ttkcal.pack(expand=1, fill='both')

    # Add button widget to root widget.
    button = tkinter.Button(root, text='OK',
                            command=root.destroy)
    button.pack(side='top', fill='both')

    # 'root' window (widget) close event handler.
    root.protocol('WM_DELETE_WINDOW',
                  lambda arg=root: on_closing(arg))
    root.mainloop()
    gc.collect()
    return ttkcal.selection

def result_window(title='',
                  comment='',
                  link=None):
    """
    Creates GUI result window, which indicates
    finish of the analysis.

    Args:
        title (str, default=''): root widget title;
        comment (str, default=''): comment to root widget;
        link (str, default=''): path to local dir to be opened
                                by button click.
    """

    # Create root widget and set title and geometry.
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

    # Add 'Exit' button widget to root widget.
    button = tkinter.Button(root, text='Exit',
                            command=root.destroy)
    button.pack(side='bottom', fill='both')

    # Add 'Open result folder' button to root widget.
    if link != None:
        button = tkinter.Button(root, text='Open result folder',
                                command=lambda: open_result_folder(root, link))
        button.pack(side='top', fill='both')

    # 'root' window (widget) close event handler.
    root.protocol('WM_DELETE_WINDOW',
                  lambda arg=root: on_closing(arg))
    root.mainloop()
    gc.collect()
    
def open_result_folder(root, link):
    """
    Function executes a child program in a new process.
    This case executes Windows Explorer to open the link.

    Args:
        root (Tk object): Toplevel widget of Tk, main window of an app;
        link (Path): path to dir to be opened.
    """

    if link.is_dir():
        subprocess.Popen(f'explorer {str(link)}')

    root.destroy()

def on_closing(root):
    """
    'root' window (widget) close event handler,
    i.e. clicking the 'X' button handler.

    Args:
        root (Tk object): Toplevel widget of Tk, main window of an app;
    """

    if messagebox.askokcancel('Quit', 'Do you want to quit?'):

        print('Exiting...')
        root.destroy()
        exit()

if __name__ == '__main__':
    calendar_window(title="Result window", comment=DESCRIPTION)
    calendar_window(title="Result window", comment=DESCRIPTION)
    # result_window(title="Result window", comment=DESCRIPTION, link=r"C:\Users\artemk\Downloads")
