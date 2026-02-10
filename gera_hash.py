import hashlib

senha = "123"
print(hashlib.sha256(senha.encode()).hexdigest())

#python gera_hash.py

#atualizar o banco no SQLite

# UPDATE usuarios
# SET senha_hash = 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3'
# WHERE usuario = 'teste3';