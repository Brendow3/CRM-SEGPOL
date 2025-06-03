from tkinter import *
from tkinter import ttk
from database.db import get_connection
from datetime import datetime

def load_chamados(frame):
    for widget in frame.winfo_children():
        widget.destroy()

    # Formulário
    form_frame = Frame(frame)
    form_frame.pack(pady=10)

    campos = {
        "Título": Entry(form_frame, width=40),
        "Descrição": Entry(form_frame, width=40),
        "Status": Entry(form_frame, width=40),
        "Prioridade": Entry(form_frame, width=40),
        "Cliente ID": Entry(form_frame, width=40)
    }

    for i, (label, entry) in enumerate(campos.items()):
        Label(form_frame, text=label + ":").grid(row=i, column=0, sticky="e")
        entry.grid(row=i, column=1)

    selected_id = StringVar()

    def salvar_chamado():
        values = tuple(e.get() for e in campos.values())
        if not all(values):
            # Validação simples
            print("Preencha todos os campos.")
            return

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO chamados (titulo, descricao, status, prioridade, cliente_id)
            VALUES (?, ?, ?, ?, ?)
        ''', values)
        chamado_id = cursor.lastrowid

        # Inserir no histórico de atendimentos
        descricao_historico = f"Chamado criado: {campos['Descrição'].get()}"
        cursor.execute('''
            INSERT INTO historico_atendimentos (cliente_id, data, descricao)
            VALUES (?, ?, ?)
        ''', (campos["Cliente ID"].get(), datetime.today().strftime("%Y-%m-%d"), descricao_historico))

        conn.commit()
        conn.close()
        carregar_chamados()
        limpar_campos()

    def atualizar_chamado():
        if not selected_id.get():
            return
        values = tuple(e.get() for e in campos.values())
        if not all(values):
            print("Preencha todos os campos.")
            return

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE chamados SET titulo=?, descricao=?, status=?, prioridade=?, cliente_id=?
            WHERE id=?
        ''', values + (selected_id.get(),))

        # Atualizar histórico de atendimento: inserir novo registro indicando atualização
        descricao_historico = f"Chamado atualizado: {campos['Descrição'].get()}"
        cursor.execute('''
            INSERT INTO historico_atendimentos (cliente_id, data, descricao)
            VALUES (?, ?, ?)
        ''', (campos["Cliente ID"].get(), datetime.today().strftime("%Y-%m-%d"), descricao_historico))

        conn.commit()
        conn.close()
        carregar_chamados()
        limpar_campos()

    def limpar_campos():
        for entry in campos.values():
            entry.delete(0, END)
        selected_id.set("")

    Button(form_frame, text="Salvar Novo", command=salvar_chamado).grid(row=len(campos), column=0, pady=10)
    Button(form_frame, text="Atualizar Selecionado", command=atualizar_chamado).grid(row=len(campos), column=1)

    # Campo de busca
    busca_frame = Frame(frame)
    busca_frame.pack(pady=10)

    Label(busca_frame, text="Buscar Chamado:").pack(side=LEFT)
    busca_entry = Entry(busca_frame)
    busca_entry.pack(side=LEFT)

    def buscar_chamados():
        termo = busca_entry.get()
        carregar_chamados(termo)

    Button(busca_frame, text="Buscar", command=buscar_chamados).pack(side=LEFT)

    # Tabela
    colunas = ("id", "titulo", "descricao", "status", "prioridade", "cliente_id")
    tabela = ttk.Treeview(frame, columns=colunas, show="headings")
    for col in colunas:
        tabela.heading(col, text=col.title())
        tabela.column(col, width=100, anchor='center')
    tabela.pack(fill="both", expand=True)

    def carregar_chamados(filtro=""):
        for row in tabela.get_children():
            tabela.delete(row)

        conn = get_connection()
        cursor = conn.cursor()
        if filtro:
            filtro_like = f"%{filtro}%"
            cursor.execute('''
                SELECT id, titulo, descricao, status, prioridade, cliente_id
                FROM chamados
                WHERE titulo LIKE ? OR descricao LIKE ? OR status LIKE ? OR prioridade LIKE ?
            ''', (filtro_like, filtro_like, filtro_like, filtro_like))
        else:
            cursor.execute("SELECT id, titulo, descricao, status, prioridade, cliente_id FROM chamados")

        chamados = cursor.fetchall()
        conn.close()

        for chamado in chamados:
            tabela.insert("", "end", values=chamado)

    def on_item_select(event):
        item = tabela.focus()
        if not item:
            return
        values = tabela.item(item, "values")
        selected_id.set(values[0])
        campos["Título"].delete(0, END)
        campos["Título"].insert(0, values[1])
        campos["Descrição"].delete(0, END)
        campos["Descrição"].insert(0, values[2])
        campos["Status"].delete(0, END)
        campos["Status"].insert(0, values[3])
        campos["Prioridade"].delete(0, END)
        campos["Prioridade"].insert(0, values[4])
        campos["Cliente ID"].delete(0, END)
        campos["Cliente ID"].insert(0, values[5])

    tabela.bind("<<TreeviewSelect>>", on_item_select)

    # Botão de exclusão
    def excluir_chamado():
        item = tabela.focus()
        if not item:
            return
        chamado_id = tabela.item(item, "values")[0]

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM chamados WHERE id = ?", (chamado_id,))

        # Inserir no histórico que o chamado foi excluído
        descricao_historico = f"Chamado ID {chamado_id} excluído"
        cursor.execute('''
            INSERT INTO historico_atendimentos (cliente_id, data, descricao)
            VALUES (?, ?, ?)
        ''', (campos["Cliente ID"].get(), datetime.today().strftime("%Y-%m-%d"), descricao_historico))

        conn.commit()
        conn.close()
        carregar_chamados()
        limpar_campos()

    Button(frame, text="Excluir Selecionado", command=excluir_chamado).pack(pady=5)

    carregar_chamados()
