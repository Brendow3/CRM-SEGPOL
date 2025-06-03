from tkinter import Label, Frame
from database.db import get_connection

def load_dashboard(frame):
    # Limpa widgets anteriores
    for widget in frame.winfo_children():
        widget.destroy()

    # Conexão com o banco de dados
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Consultas
        cursor.execute("SELECT COUNT(*) FROM clientes")
        total_clientes = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM chamados WHERE status = 'ativo'")
        chamados_ativos = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM visitas")
        total_visitas = cursor.fetchone()[0]
    except Exception as e:
        total_clientes = chamados_ativos = total_visitas = "Erro"
        print("Erro ao carregar indicadores:", e)
    finally:
        conn.close()

    # Título
    Label(frame, text="📊 Painel de Indicadores", font=("Arial", 18, "bold"), fg="#003366").pack(pady=20)

    # Indicadores
    indicadores_frame = Frame(frame)
    indicadores_frame.pack(pady=10)

    Label(indicadores_frame, text=f"👤 Total de Clientes: {total_clientes}", font=("Arial", 14)).pack(pady=5)
    Label(indicadores_frame, text=f"🛠️ Chamados Ativos: {chamados_ativos}", font=("Arial", 14)).pack(pady=5)
    Label(indicadores_frame, text=f"📅 Visitas Técnicas: {total_visitas}", font=("Arial", 14)).pack(pady=5)
