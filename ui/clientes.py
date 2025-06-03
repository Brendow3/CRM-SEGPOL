from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from database.db import get_connection
from tkinter import filedialog
import os
import shutil
from datetime import datetime

def load_clientes(frame):
    for widget in frame.winfo_children():
        widget.destroy()

    # Formulário
    form_frame = Frame(frame)
    form_frame.pack(pady=10)

    campos = {
        "Nome": Entry(form_frame, width=40),
        "Endereço": Entry(form_frame, width=40),
        "Telefone": Entry(form_frame, width=40),
        "Email": Entry(form_frame, width=40),
        "CPF/CNPJ": Entry(form_frame, width=40),
        "Status": Entry(form_frame, width=40),
        "Prioridade": Entry(form_frame, width=40)
    }

    for i, (label, entry) in enumerate(campos.items()):
        Label(form_frame, text=label + ":").grid(row=i, column=0, sticky="e")
        entry.grid(row=i, column=1)

    selected_id = StringVar()

    def salvar_cliente():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO clientes (nome, endereco, telefone, email, cpf_cnpj, status, prioridade)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', tuple(e.get() for e in campos.values()))
        conn.commit()
        conn.close()
        carregar_clientes()
        limpar_campos()

    def atualizar_cliente():
        if not selected_id.get():
            return
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE clientes SET nome=?, endereco=?, telefone=?, email=?, cpf_cnpj=?, status=?, prioridade=?
            WHERE id=?
        ''', tuple(e.get() for e in campos.values()) + (selected_id.get(),))
        conn.commit()
        conn.close()
        carregar_clientes()
        limpar_campos()

    def limpar_campos():
        for entry in campos.values():
            entry.delete(0, END)
        selected_id.set("")

    Button(form_frame, text="Salvar Novo", command=salvar_cliente).grid(row=len(campos), column=0, pady=10)
    Button(form_frame, text="Atualizar Selecionado", command=atualizar_cliente).grid(row=len(campos), column=1)

    busca_frame = Frame(frame)
    busca_frame.pack(pady=10)

    Label(busca_frame, text="Buscar Cliente:").pack(side=LEFT)
    busca_entry = Entry(busca_frame)
    busca_entry.pack(side=LEFT)

    def buscar_clientes():
        termo = busca_entry.get()
        carregar_clientes(termo)

    Button(busca_frame, text="Buscar", command=buscar_clientes).pack(side=LEFT)

    colunas = ("id", "nome", "endereco", "telefone", "email", "cpf_cnpj", "status", "prioridade")
    tabela = ttk.Treeview(frame, columns=colunas, show="headings")
    for col in colunas:
        tabela.heading(col, text=col.title())
    tabela.pack(fill="both", expand=True)

    def carregar_clientes(filtro=""):
        for row in tabela.get_children():
            tabela.delete(row)

        conn = get_connection()
        cursor = conn.cursor()
        if filtro:
            cursor.execute("""
                SELECT id, nome, endereco, telefone, email, cpf_cnpj, status, prioridade
                FROM clientes WHERE nome LIKE ?
            """, (f"%{filtro}%",))
        else:
            cursor.execute("SELECT id, nome, endereco, telefone, email, cpf_cnpj, status, prioridade FROM clientes")
        for row in cursor.fetchall():
            tabela.insert("", "end", values=row)
        conn.close()

    def on_item_select(event):
        item = tabela.focus()
        if not item:
            return
        values = tabela.item(item, "values")
        selected_id.set(values[0])
        for key, value in zip(campos.keys(), values[1:]):
            campos[key].delete(0, END)
            campos[key].insert(0, value)

    tabela.bind("<<TreeviewSelect>>", on_item_select)

    def excluir_cliente():
        item = tabela.focus()
        if not item:
            return
        cliente_id = tabela.item(item, "values")[0]
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM clientes WHERE id = ?", (cliente_id,))
        conn.commit()
        conn.close()
        carregar_clientes()
        limpar_campos()

    Button(frame, text="Excluir Selecionado", command=excluir_cliente).pack(pady=5)

    # Botão para ver funcionalidades adicionais
    def abrir_detalhes_cliente():
        item = tabela.focus()
        if not item:
            return
        cliente_id = tabela.item(item, "values")[0]
        abrir_detalhes(cliente_id)

    Button(frame, text="Ver Detalhes do Cliente", command=abrir_detalhes_cliente).pack(pady=10)

    carregar_clientes()

def preencher_aba_anexos(frame, cliente_id):
        uploads_dir = "uploads"
        os.makedirs(uploads_dir, exist_ok=True)

        def carregar_anexos():
            for row in tree.get_children():
                tree.delete(row)

            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, nome_arquivo, caminho_arquivo, data_envio FROM anexos WHERE cliente_id = ?", (cliente_id,))
            for row in cursor.fetchall():
                tree.insert("", "end", iid=row[0], values=row[1:])
            conn.close()

        def enviar_arquivo():
            arquivo = filedialog.askopenfilename()
            if not arquivo:
                return

            nome_arquivo = os.path.basename(arquivo)
            destino = os.path.join(uploads_dir, nome_arquivo)

            # Evita sobrescrever
            if os.path.exists(destino):
                messagebox.showwarning("Aviso", "Arquivo já enviado.")
                return

            shutil.copy(arquivo, destino)

            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO anexos (cliente_id, nome_arquivo, caminho_arquivo, data_envio) VALUES (?, ?, ?, ?)",
                        (cliente_id, nome_arquivo, destino, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()
            conn.close()
            carregar_anexos()

        def abrir_arquivo():
            selected = tree.focus()
            if not selected:
                return
            caminho = tree.item(selected, "values")[1]
            os.startfile(caminho)

        def excluir_arquivo():
            selected = tree.focus()
            if not selected:
                return
            caminho = tree.item(selected, "values")[1]
            if os.path.exists(caminho):
                os.remove(caminho)
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM anexos WHERE id = ?", (selected,))
            conn.commit()
            conn.close()
            carregar_anexos()

        # Botões
        btn_upload = Button(frame, text="Enviar Arquivo", command=enviar_arquivo)
        btn_upload.pack(pady=5)

        btn_abrir = Button(frame, text="Abrir Selecionado", command=abrir_arquivo)
        btn_abrir.pack(pady=2)

        btn_excluir = Button(frame, text="Excluir Selecionado", command=excluir_arquivo)
        btn_excluir.pack(pady=2)

        # Tabela
        tree = ttk.Treeview(frame, columns=["nome", "caminho", "data"], show="headings")
        tree.heading("nome", text="Nome do Arquivo")
        tree.heading("caminho", text="Caminho")
        tree.heading("data", text="Data Envio")

        tree.column("nome", width=200)
        tree.column("caminho", width=300)
        tree.column("data", width=120)

        tree.pack(fill='both', expand=True, pady=5, padx=5)

        carregar_anexos()

def abrir_detalhes(cliente_id):
    detalhes = Toplevel()
    detalhes.title("Detalhes do Cliente")
    detalhes.geometry("800x500")

    notebook = ttk.Notebook(detalhes)
    notebook.pack(fill='both', expand=True)

    abas = {
        "Histórico de Atendimentos": Frame(notebook),
        "Visitas Técnicas": Frame(notebook),
        "Negociações": Frame(notebook),
        "Contratos de Serviços": Frame(notebook)
    }

    for nome, frame in abas.items():
        notebook.add(frame, text=nome)
        preencher_aba(frame, nome, cliente_id)

    # Adiciona a aba de Anexos
    frame_anexos = Frame(notebook)
    notebook.add(frame_anexos, text="Anexos")
    preencher_aba_anexos(frame_anexos, cliente_id)

    btn_fechar = ttk.Button(detalhes, text="Fechar", command=detalhes.destroy)
    btn_fechar.pack(pady=5)

def preencher_aba(frame, tipo, cliente_id):
    # Limpa frame para evitar sobreposição
    for widget in frame.winfo_children():
        widget.destroy()

    # Estrutura do frame: formulário em cima, tabela embaixo
    form_frame = Frame(frame)
    form_frame.pack(fill='x', pady=5, padx=5)

    tabela_frame = Frame(frame)
    tabela_frame.pack(fill='both', expand=True, pady=5, padx=5)

    # Define campos conforme o tipo
    if tipo == "Histórico de Atendimentos":
        campos = ["data", "descricao"]
        colunas = ["Data", "Descrição"]
        tabela_cols = campos
    elif tipo == "Visitas Técnicas":
        campos = ["data", "tecnico", "descricao"]
        colunas = ["Data", "Técnico", "Descrição"]
        tabela_cols = campos
    elif tipo == "Negociações":
        campos = ["data", "descricao", "status"]
        colunas = ["Data", "Descrição", "Status"]
        tabela_cols = campos
    elif tipo == "Contratos de Serviços":
        campos = ["tipo_servico", "data_inicio", "data_fim", "status"]
        colunas = ["Tipo Serviço", "Início", "Fim", "Status"]
        tabela_cols = campos
    else:
        return

    entradas = {}
    for i, campo in enumerate(campos):
        lbl = Label(form_frame, text=colunas[i] + ":")
        lbl.grid(row=0, column=i*2, sticky='e', padx=2)
        entry = Entry(form_frame, width=20)
        entry.grid(row=0, column=i*2 + 1, padx=2)
        entradas[campo] = entry

    selected_id = StringVar()

    def limpar_campos():
        for e in entradas.values():
            e.delete(0, END)
        selected_id.set("")
        btn_filtrar = Button(form_frame, text="Filtrar", command=filtrar_registros)
        btn_filtrar.grid(row=1, column=3, pady=5, padx=2)

    def carregar_registros():
        for row in tree.get_children():
            tree.delete(row)

        try:
            conn = get_connection()
            cursor = conn.cursor()

            # Consulta conforme aba e cliente
            if tipo == "Histórico de Atendimentos":
                cursor.execute("SELECT id, data, descricao FROM historico_atendimentos WHERE cliente_id = ?", (cliente_id,))
            elif tipo == "Visitas Técnicas":
                cursor.execute("SELECT id, data, tecnico, descricao FROM visitas_tecnicas WHERE cliente_id = ?", (cliente_id,))
            elif tipo == "Negociações":
                cursor.execute("SELECT id, data, descricao, status FROM negociacoes WHERE cliente_id = ?", (cliente_id,))
            elif tipo == "Contratos de Serviços":
                cursor.execute("SELECT id, tipo_servico, data_inicio, data_fim, status FROM contratos_servicos WHERE cliente_id = ?", (cliente_id,))
            else:
                return

            for row in cursor.fetchall():
                # Ignora id na exibição, só usa para seleção
                tree.insert("", "end", iid=row[0], values=row[1:])
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar registros: {e}")
        finally:
            conn.close()

    def salvar_registro():
        valores = [e.get() for e in entradas.values()]
        if any(v.strip() == "" for v in valores):
            messagebox.showwarning("Aviso", "Preencha todos os campos.")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            if tipo == "Histórico de Atendimentos":
                cursor.execute("INSERT INTO historico_atendimentos (cliente_id, data, descricao) VALUES (?, ?, ?)",
                               (cliente_id, valores[0], valores[1]))
            elif tipo == "Visitas Técnicas":
                cursor.execute("INSERT INTO visitas_tecnicas (cliente_id, data, tecnico, descricao) VALUES (?, ?, ?, ?)",
                               (cliente_id, valores[0], valores[1], valores[2]))
            elif tipo == "Negociações":
                cursor.execute("INSERT INTO negociacoes (cliente_id, data, descricao, status) VALUES (?, ?, ?, ?)",
                               (cliente_id, valores[0], valores[1], valores[2]))
            elif tipo == "Contratos de Serviços":
                cursor.execute("INSERT INTO contratos_servicos (cliente_id, tipo_servico, data_inicio, data_fim, status) VALUES (?, ?, ?, ?, ?)",
                               (cliente_id, valores[0], valores[1], valores[2], valores[3]))
            else:
                return

            conn.commit()
            carregar_registros()
            limpar_campos()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar registro: {e}")
        finally:
            conn.close()

    def atualizar_registro():
        if not selected_id.get():
            messagebox.showwarning("Aviso", "Selecione um registro para atualizar.")
            return
        valores = [e.get() for e in entradas.values()]
        if any(v.strip() == "" for v in valores):
            messagebox.showwarning("Aviso", "Preencha todos os campos.")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            if tipo == "Histórico de Atendimentos":
                cursor.execute("UPDATE historico_atendimentos SET data=?, descricao=? WHERE id=?",
                               (valores[0], valores[1], selected_id.get()))
            elif tipo == "Visitas Técnicas":
                cursor.execute("UPDATE visitas_tecnicas SET data=?, tecnico=?, descricao=? WHERE id=?",
                               (valores[0], valores[1], valores[2], selected_id.get()))
            elif tipo == "Negociações":
                cursor.execute("UPDATE negociacoes SET data=?, descricao=?, status=? WHERE id=?",
                               (valores[0], valores[1], valores[2], selected_id.get()))
            elif tipo == "Contratos de Serviços":
                cursor.execute("UPDATE contratos_servicos SET tipo_servico=?, data_inicio=?, data_fim=?, status=? WHERE id=?",
                               (valores[0], valores[1], valores[2], valores[3], selected_id.get()))
            else:
                return

            conn.commit()
            carregar_registros()
            limpar_campos()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar registro: {e}")
        finally:
            conn.close()

    def excluir_registro():
        if not selected_id.get():
            messagebox.showwarning("Aviso", "Selecione um registro para excluir.")
            return

        if not messagebox.askyesno("Confirmação", "Deseja realmente excluir o registro selecionado?"):
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            if tipo == "Histórico de Atendimentos":
                cursor.execute("DELETE FROM historico_atendimentos WHERE id=?", (selected_id.get(),))
            elif tipo == "Visitas Técnicas":
                cursor.execute("DELETE FROM visitas_tecnicas WHERE id=?", (selected_id.get(),))
            elif tipo == "Negociações":
                cursor.execute("DELETE FROM negociacoes WHERE id=?", (selected_id.get(),))
            elif tipo == "Contratos de Serviços":
                cursor.execute("DELETE FROM contratos_servicos WHERE id=?", (selected_id.get(),))
            else:
                return
            conn.commit()
            carregar_registros()
            limpar_campos()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao excluir registro: {e}")
        finally:
            conn.close()

    # Botões do formulário
    btn_salvar = Button(form_frame, text="Salvar Novo", command=salvar_registro)
    btn_salvar.grid(row=1, column=0, pady=5, padx=2)

    btn_atualizar = Button(form_frame, text="Atualizar Selecionado", command=atualizar_registro)
    btn_atualizar.grid(row=1, column=1, pady=5, padx=2)

    btn_limpar = Button(form_frame, text="Limpar Campos", command=limpar_campos)
    btn_limpar.grid(row=1, column=2, pady=5, padx=2)

    # Treeview para dados
    tree = ttk.Treeview(tabela_frame, columns=tabela_cols, show="headings")
    for c, nome_col in zip(tabela_cols, colunas):
        tree.heading(c, text=nome_col)
        tree.column(c, width=120, anchor='w')
    tree.pack(fill='both', expand=True)

    # Quando selecionar uma linha, preencher os campos
    def on_tree_select(event):
        selected = tree.focus()
        if not selected:
            return
        selected_id.set(selected)
        valores = tree.item(selected, "values")
        for i, campo in enumerate(campos):
            entradas[campo].delete(0, END)
            entradas[campo].insert(0, valores[i])

    tree.bind("<<TreeviewSelect>>", on_tree_select)

    btn_excluir = Button(frame, text="Excluir Selecionado", command=excluir_registro)
    btn_excluir.pack(pady=5)

    carregar_registros()
    
    def filtrar_registros():
        for row in tree.get_children():
            tree.delete(row)

        filtros = {campo: entrada.get().strip() for campo, entrada in entradas.items() if entrada.get().strip()}

        if not filtros:
            carregar_registros()
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()

            query_base = ""
            params = []

            if tipo == "Histórico de Atendimentos":
                query_base = "SELECT id, data, descricao FROM historico_atendimentos WHERE cliente_id=?"
            elif tipo == "Visitas Técnicas":
                query_base = "SELECT id, data, tecnico, descricao FROM visitas_tecnicas WHERE cliente_id=?"
            elif tipo == "Negociações":
                query_base = "SELECT id, data, descricao, status FROM negociacoes WHERE cliente_id=?"
            elif tipo == "Contratos de Serviços":
                query_base = "SELECT id, tipo_servico, data_inicio, data_fim, status FROM contratos_servicos WHERE cliente_id=?"
            else:
                return

            params.append(cliente_id)

            for campo, valor in filtros.items():
                query_base += f" AND {campo} LIKE ?"
                params.append(f"%{valor}%")

            cursor.execute(query_base, params)

            for row in cursor.fetchall():
                tree.insert("", "end", iid=row[0], values=row[1:])

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao filtrar registros: {e}")
        finally:
            conn.close()
            
    btn_filtrar = Button(form_frame, text="Filtrar", command=filtrar_registros)
    btn_filtrar.grid(row=1, column=3, pady=5, padx=2)

    