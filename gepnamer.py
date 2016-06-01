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
        self.rename_map = None

        # Show name
        self.var_show_name = tkinter.StringVar()
        ttk.Label(frame, text='Show name:').grid(row=1, column=1)
        ttk.Entry(frame, textvariable=self.var_show_name).grid(
                row=1, column=2)
        ttk.Button(frame, text='Load', command=self.load_show).grid(
                row=1, column=3)

        # Target files
        self.var_target = tkinter.StringVar()
        ttk.Label(frame, text='Target(s):').grid(row=2, column=1)
        ttk.Entry(frame, textvariable=self.var_target).grid(row=2, column=2)
        ttk.Button(frame, text='...', command=self.choose_dir).grid(
                row=2, column=3)

        ttk.Button(frame, text='Generate', command=self.generate).grid(
                row=1, column=4, rowspan=2)

        self.tree = ttk.Treeview(frame, columns=('New name',))
        self.tree.grid(row=3, column=1, columnspan=4)

        self.button_rename = ttk.Button(
                frame, text='Rename', command=self.rename)
        self.button_rename.grid(row=4, column=3)
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

        for key in self.rename_map:
            old_name = os.path.basename(key)
            new_name = os.path.basename(self.rename_map[key])
            self.tree.insert('', 'end', text=old_name, values=new_name)

        self.button_rename.state(["!disabled"])

    def rename(self):
        do_renaming(self.rename_map)
        messagebox.showinfo('Rename', 'Rename complete!')


def umain():
    do_renaming(rename_map)

def main():
    app = Application()
    app.var_show_name.set('Friends')
    app.var_target.set('test')
    app.root.mainloop()


if __name__ == '__main__':
    main()
