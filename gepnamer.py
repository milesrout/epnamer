from epnamer import *
import tkinter
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox

class Application():
    def __init__(self):
        self.root = tkinter.Tk()
        self.root.title('gEpnamer')
        self.root.geometry('800x600')
        self.initialize()

    def initialize(self):
        frame = ttk.Frame(self.root)
        frame.pack(expand=True, fill='both')

        frame.grid_columnconfigure(2, weight=1)
        frame.grid_rowconfigure(3, weight=1)

        self.guide = None
        self.filepaths = None
        self.rename_map = None

        pad = {'padx': 5, 'pady': 2}

        # Show name
        self.var_show_name = tkinter.StringVar()
        ttk.Label(frame, text='Show name:').grid(
                row=1, column=1, sticky='e', **pad)
        ttk.Entry(frame, textvariable=self.var_show_name).grid(
                row=1, column=2, sticky='ew', **pad)
        ttk.Button(frame, text='Load', command=self.load_show).grid(
                row=1, column=3, **pad)

        # Target files
        self.var_target = tkinter.StringVar()
        ttk.Label(frame, text='Target(s):').grid(
                row=2, column=1, sticky='e', **pad)
        ttk.Entry(frame, textvariable=self.var_target).grid(
                row=2, column=2, sticky='ew', **pad)
        ttk.Button(frame, text='...', command=self.choose_dir).grid(
                row=2, column=3, **pad)

        ttk.Button(frame, text='Generate', command=self.generate).grid(
                row=1, column=4, rowspan=2, **pad)

        # Rename table
        self.tree = ttk.Treeview(frame, columns=('New name',))
        self.tree.grid(row=3, column=1, columnspan=4, sticky='news', **pad)

        self.button_rename = ttk.Button(
                frame, text='Rename', command=self.rename)
        self.button_rename.grid(row=4, column=4, **pad)
        self.button_rename.state(["disabled"])

    def load_show(self):
        try:
            self.guide = tvmaze_guide(self.var_show_name.get())
        except urllib.error.HTTPError:
            self.guide = None
            self.clear()
        if not self.guide:
            messagebox.showerror('Load show', 'No show guide found')

    def choose_dir(self):
        path = filedialog.askdirectory()
        if path:
            self.var_target.set(path)

    def clear(self):
        self.button_rename.state(["disabled"])
        self.tree.delete(*self.tree.get_children())

    def generate(self):
        if not self.guide:
            self.load_show()
            if not self.guide:
                return

        filepaths = list(recursive_iter_paths((self.var_target.get(),)))
        self.rename_map = get_rename_map(filepaths, self.guide)
        if not self.rename_map:
            messagebox.showerror('Load targets', 'No files to rename')
            self.clear()
            return

        for key in sorted(self.rename_map, key=os.path.basename):
            old_name = os.path.basename(key)
            new_name = os.path.basename(self.rename_map[key])
            self.tree.insert('', 'end', text=old_name, values=new_name)

        self.button_rename.state(["!disabled"])

    def rename(self):
        do_renaming(self.rename_map)
        messagebox.showinfo('Rename', 'Rename complete!')

def main():
    app = Application()
    app.var_show_name.set('Friends')
    app.var_target.set('test')

    import sys
    def close(event):
        app.root.withdraw()
        sys.exit()
    app.root.bind('<Escape>', close)

    app.root.mainloop()


if __name__ == '__main__':
    main()
