from gepnamer import *

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
