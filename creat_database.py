import sqlite3

conn = sqlite3.connect("contratos.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS contratos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa TEXT,
    instalacao TEXT,
    area_total REAL,
    municipio TEXT,
    uf TEXT,
    acessante TEXT,
    videomonitoramento TEXT,
    controle_acesso TEXT,
    pedido_sa TEXT,
    dt_inicio TEXT,
    dt_fim TEXT,
    servico_contratado TEXT,
    registro_ronda TEXT,
    horario_posto TEXT,
    qtd_postos INTEGER,
    qtd_agentes INTEGER,
    vlr_unit_agente REAL,
    vlr_unit_posto REAL,
    vlr_mensal_atual REAL,
    total_postos REAL,
    total_geral REAL
)
""")

cursor.execute("""
CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT UNIQUE NOT NULL,
    senha_hash TEXT NOT NULL,
    perfil TEXT DEFAULT 'user',
    ativo INTEGER DEFAULT 1,
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()
conn.close()

print("Tabelas criadas com sucesso!")