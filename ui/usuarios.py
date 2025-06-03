from tkinter import *
from tkinter import ttk
from database.db import get_connection

def load_usuarios(frame, usuario_logado):
    for widget in frame.winfo_children():
        widget.destroy()

    Label(frame, text="Gestão de Usuários", font=("Arial", 14)).pack(pady=10)

    is_admin = usuario_logado['tipo'] == 'admin'
    usuario_selecionado_id = StringVar()

    if is_admin:
        form_frame = Frame(frame)
        form_frame.pack(pady=10)

        Label(form_frame, text="Nome:").grid(row=0, column=0)
        nome_entry = Entry(form_frame)
        nome_entry.grid(row=0, column=1)

        Label(form_frame, text="Email:").grid(row=1, column=0)
        email_entry = Entry(form_frame)
        email_entry.grid(row=1, column=1)

        Label(form_frame, text="Senha:").grid(row=2, column=0)
        senha_entry = Entry(form_frame, show="*")
        senha_entry.grid(row=2, column=1)

        Label(form_frame, text="Tipo:").grid(row=3, column=0)
        tipo_cb = ttk.Combobox(form_frame, values=["admin", "comum"])
        tipo_cb.grid(row=3, column=1)

        def limpar_formulario():
            nome_entry.delete(0, END)
            email_entry.delete(0, END)
            senha_entry.delete(0, END)
            tipo_cb.set("")
            usuario_selecionado_id.set("")

        def salvar_usuario():
            nome = nome_entry.get()
            email = email_entry.get()
            senha = senha_entry.get()
            tipo = tipo_cb.get() or "comum"

            conn = get_connection()
            cursor = conn.cursor()

            if usuario_selecionado_id.get():
                cursor.execute('''
                    UPDATE usuarios
                    SET nome=?, email=?, senha=?, tipo=?
                    WHERE id=?
                ''', (nome, email, senha, tipo, usuario_selecionado_id.get()))
            else:
                cursor.execute('''
                    INSERT INTO usuarios (nome, email, senha, tipo)
                    VALUES (?, ?, ?, ?)
                ''', (nome, email, senha, tipo))
            conn.commit()
            conn.close()
            limpar_formulario()
            carregar_usuarios()

        def excluir_usuario():
            if not usuario_selecionado_id.get():
                return
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM usuarios WHERE id = ?", (usuario_selecionado_id.get(),))
            conn.commit()
            conn.close()
            limpar_formulario()
            carregar_usuarios()

        Button(form_frame, text="Salvar / Atualizar", command=salvar_usuario).grid(row=4, column=0, pady=5)
        Button(form_frame, text="Excluir", command=excluir_usuario).grid(row=4, column=1, pady=5)

    # Tabela de usuários
    tabela = ttk.Treeview(frame, columns=("id", "nome", "email", "tipo"), show="headings")
    tabela.heading("id", text="ID")
    tabela.heading("nome", text="Nome")
    tabela.heading("email", text="Email")
    tabela.heading("tipo", text="Tipo")
    tabela.column("id", width=30)
    tabela.pack(fill="both", expand=True)

    def carregar_usuarios():
        for row in tabela.get_children():
            tabela.delete(row)

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, email, tipo FROM usuarios")
        usuarios = cursor.fetchall()
        conn.close()
        print("Usuários encontrados:", usuarios)
        for user in usuarios:
            tabela.insert("", "end", values=user)

    def selecionar_usuario(event):
        if not is_admin:
            return

        selected = tabela.selection()
        if not selected:
            return
        item = tabela.item(selected[0])
        user = item['values']
        usuario_selecionado_id.set(user[0])

        nome_entry.delete(0, END)
        nome_entry.insert(0, user[1])

        email_entry.delete(0, END)
        email_entry.insert(0, user[2])

        senha_entry.delete(0, END)
        senha_entry.insert(0, "")  # senha oculta

        tipo_cb.set(user[3])

    tabela.bind("<<TreeviewSelect>>", selecionar_usuario)

    carregar_usuarios()
