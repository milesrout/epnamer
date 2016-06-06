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

        pad = {'padx': 3, 'pady': 2}

        # Target files
        self.var_target = tkinter.StringVar()
        ttk.Label(frame, text='Target(s):').grid(
                row=1, column=1, sticky='e', **pad)
        ttk.Entry(frame, textvariable=self.var_target).grid(
                row=1, column=2, sticky='ew', **pad)
        ttk.Button(frame, text='...', command=self.choose_dir).grid(
                row=1, column=3, **pad)

        # Show name
        self.var_show_name = tkinter.StringVar()
        ttk.Label(frame, text='Show name:').grid(
                row=2, column=1, sticky='e', **pad)
        ttk.Entry(frame, textvariable=self.var_show_name).grid(
                row=2, column=2, sticky='ew', **pad)

        # Generate button
        ttk.Button(frame, text='Generate', command=self.generate).grid(
                row=2, column=3, **pad)

        # Rename table
        table = ttk.Frame(frame)
        table.grid(row=3, column=1, columnspan=3, sticky='news', **pad)

        vscroll = ttk.Scrollbar(table)
        vscroll.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        hscroll = ttk.Scrollbar(table, orient=tkinter.HORIZONTAL)
        hscroll.pack(side=tkinter.BOTTOM, fill=tkinter.X)

        self.tree = ttk.Treeview(table, columns=('New name',),
                yscrollcommand=vscroll.set, xscrollcommand=hscroll.set)
        self.tree.pack(expand=tkinter.YES, fill=tkinter.BOTH)
        vscroll.config(command=self.tree.yview)
        hscroll.config(command=self.tree.xview)

        # Undo script
        self.var_undo_script = tkinter.StringVar()
        ttk.Label(frame, text='Undo script:').grid(
                row=4, column=1, sticky='e', **pad)
        ttk.Entry(frame, textvariable=self.var_undo_script).grid(
                row=4, column=2, sticky='ew', **pad)
        ttk.Button(frame, text='...', command=self.choose_undo).grid(
                row=4, column=3, **pad)

        # Rename button
        self.button_rename = ttk.Button(
                frame, text='Rename', command=self.rename)
        self.button_rename.grid(row=5, column=3, **pad)
        self.button_rename.state(["disabled"])

        # Data source
        guide_credit = "Episode guide: " + tvmaze_guide.api_source(None)
        source_credit = "Source code: Louis Warren <http://git.lsw.nz/epnamer>"
        ttk.Label(frame, text=guide_credit).grid(
                row=5, column=1, columnspan=2, sticky='e', **pad)
        ttk.Label(frame, text=source_credit).grid(
                row=5, column=1, columnspan=2, sticky='w', **pad)

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

    def choose_undo(self):
        if os.name == 'nt':
            undo_name = 'epnamer-undo.bat'
        else:
            undo_name = 'epnamer-undo.sh'
        filename = filedialog.asksaveasfilename(initialfile=undo_name)
        self.var_undo_script.set(filename)

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
        if not self.var_undo_script.get():
            if not messagebox.askokcancel('No undo script',
                    'Continue without being able to undo changes?'):
                return
            do_renaming(self.rename_map)
        else:
            with open(self.var_undo_script.get(), 'w') as undo_file:
                do_renaming(self.rename_map, undo_file)

        messagebox.showinfo('Rename', 'Rename complete!')
        self.clear()

def main():
    app = Application()
    app.root.mainloop()

if __name__ == '__main__':
    main()
