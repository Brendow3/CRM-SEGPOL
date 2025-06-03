# Ponto de entrada da aplicação
from tkinter import Tk
from ui.components import App

if __name__ == '__main__':
    root = Tk()
    app = App(root)
    root.mainloop()
