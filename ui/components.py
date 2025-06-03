from tkinter import *
from tkinter import ttk
from services.auth import autenticar
from database.db import init_db, get_connection

# Importa as funções para popular as abas
from ui.dashboard import load_dashboard
from ui.clientes import load_clientes
from ui.chamados import load_chamados
from ui.usuarios import load_usuarios

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("SEGPOL CRM")
        self.root.geometry("1000x600")
        init_db()
        self.usuario_logado = None
        self.create_login()

    def create_login(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.login_frame = Frame(self.root, padx=20, pady=20)
        self.login_frame.pack(expand=True)

        Label(self.login_frame, text="Login SEGPOL", font=("Arial", 20)).pack(pady=10)
        self.email_entry = Entry(self.login_frame, width=30)
        self.email_entry.pack(pady=5)
        self.email_entry.insert(0, "admin@admin.com")
        self.senha_entry = Entry(self.login_frame, show="*", width=30)
        self.senha_entry.pack(pady=5)
        self.senha_entry.insert(0, "admin")
        Button(self.login_frame, text="Entrar", command=self.verificar_login).pack(pady=10)

    def verificar_login(self):
        email = self.email_entry.get()
        senha = self.senha_entry.get()
        user = autenticar(email, senha)
        if user:
            self.usuario_logado = user
            self.create_main_interface()
        else:
            Label(self.login_frame, text="Credenciais inválidas", fg="red").pack()

    def create_main_interface(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True)

        self.dashboard_tab = Frame(notebook)
        self.clientes_tab = Frame(notebook)
        self.chamados_tab = Frame(notebook)
        self.usuarios_tab = Frame(notebook)

        notebook.add(self.dashboard_tab, text="Dashboard")
        notebook.add(self.clientes_tab, text="Clientes")
        notebook.add(self.chamados_tab, text="Chamados")
        notebook.add(self.usuarios_tab, text="Usuários")

        load_dashboard(self.dashboard_tab)
        load_clientes(self.clientes_tab)
        load_chamados(self.chamados_tab)
        load_usuarios(self.usuarios_tab, self.usuario_logado)
