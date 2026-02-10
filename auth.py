import hashlib
from database import fetch_all

def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

def autenticar(usuario, senha):
    senha_hash = hash_senha(senha)
    query = """
        SELECT id, usuario, perfil
        FROM usuarios
        WHERE usuario = ? AND senha_hash = ? AND ativo = 1
    """
    result = fetch_all(query, (usuario, senha_hash))
    return result[0] if result else None
