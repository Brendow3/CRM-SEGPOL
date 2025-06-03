# Autenticação
from database.db import get_connection

def autenticar(email, senha):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, email, tipo FROM usuarios WHERE email = ? AND senha = ?", (email, senha))
    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "id": row[0],
            "nome": row[1],
            "email": row[2],
            "tipo": row[3]
        }
    return None

