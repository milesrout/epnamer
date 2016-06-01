from epnamer import *
import tkinter
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox

class Application():
    def __init__(self):
        self.root = tkinter.Tk()
        self.root.title('gEpnamer')
        self.initialize()

    def initialize(self):
        frame = ttk.Frame(self.root)
        frame.pack(expand=True, fill='both')

        self.guide = None
        self.filepaths = None

        # Show name
        self.var_show_name = tkinter.StringVar()
        ttk.Label(frame, text='Show name:').grid(row=1, column=1)
        ttk.Entry(frame, textvariable=self.var_show_name).grid(
                row=1, column=2, columnspan=2)
        ttk.Button(frame, text='Load', command=self.load_show).grid(
                row=1, column=4)

        # Target files
        self.var_target = tkinter.StringVar()
        ttk.Label(frame, text='Target(s):').grid(row=2, column=1)
        ttk.Entry(frame, textvariable=self.var_target).grid(row=2, column=2)
        ttk.Button(frame, text='...', command=self.choose_dir).grid(
                row=2, column=3)
        ttk.Button(frame, text='Load', command=self.load_targets).grid(
                row=2, column=4)

        # Renames

    def load_show(self):
        try:
            self.guide = tvmaze_guide(self.var_show_name.get())
        except urllib.error.HTTPError:
            self.guide = None
        if not self.guide:
            messagebox.showerror('Load show', 'No show guide found')

    def choose_dir(self):
        path = filedialog.askdirectory()
        if path:
            self.var_target.set(path)

    def load_targets(self):
        self.filepaths = list(recursive_iter_paths((self.var_target.get(),)))
        if not self.filepaths:
            messagebox.showerror('Load targets',
                    'Nothing found in target directory')


def umain():
    try:
        guide = tvmaze_guide(sys.argv[1])
    except urllib.error.HTTPError:
        guide = None
    if not guide:
        print("Could not find show", sys.argv[1], "in database.")
        sys.exit(1)

    arg_filepaths = list(recursive_iter_paths(sys.argv[2:]))
    if not arg_filepaths:
        print("No files to rename.")
        sys.exit(1)

    rename_map = get_rename_map(arg_filepaths, guide)

    print("Performing the following renames:")
    printable_map = {f: os.path.basename(rename_map[f]) for f in rename_map}
    for basename in sorted(printable_map):
        print("{} => {}".format(basename, printable_map[basename]))
    print("")
    confirm = input("Continue? [Y/n] ").lower() in ('', 'y', 'yes')
    if not confirm:
        print("Aborted.")
        sys.exit()

    do_renaming(rename_map)

def main():
    app = Application()
    app.root.mainloop()


if __name__ == '__main__':
    main()
