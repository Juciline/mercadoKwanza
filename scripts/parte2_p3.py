"""
Parte 2 — P3-A: MongoDB Migration — Vendas por Loja (Aggregation)
       P3-B: MongoDB Migration — Clientes com Vendas Embutidas (Top 10)
"""
import mysql.connector, pymongo, time, datetime
from decimal import Decimal

def conectar_mysql():
    return mysql.connector.connect(
        host='127.0.0.1', port=3316,
        user='root', password='kwanza2024',
        database='mercadokwanza', autocommit=True
    )

def conectar_mongo():
    return pymongo.MongoClient('localhost', 27017)

# ============================================================
# P3-A: MIGRAR VENDAS PARA MONGODB + AGREGACAO
# ============================================================
print("=" * 60)
print("P3-A: MIGRACAO VENDAS -> MONGODB")
print("=" * 60)

mysql = conectar_mysql()
cur = mysql.cursor()
mongo = conectar_mongo()
db = mongo['mercadokwanza']
vendas_col = db['vendas']

# Limpar colecao anterior
vendas_col.delete_many({})

# Ler vendas do MySQL
t0 = time.time()
cur.execute("""
    SELECT v.id, v.loja_id, v.cliente_id, v.data_venda, v.total,
           iv.id, iv.produto_id, iv.qtd, iv.preco_unit, iv.desconto
    FROM VENDA v
    LEFT JOIN ITEM_VENDA iv ON v.id = iv.venda_id
    ORDER BY v.id, iv.id
""")

vendas_dict = {}
for row in cur:
    v_id = row[0]
    if v_id not in vendas_dict:
        vendas_dict[v_id] = {
            '_id': v_id,
            'loja_id': row[1],
            'cliente_id': row[2],
            'data_venda': row[3].isoformat() if isinstance(row[3], datetime.date) else str(row[3]),
            'total': float(row[4]) if row[4] else 0,
            'itens': []
        }
    if row[5]:
        vendas_dict[v_id]['itens'].append({
            'item_id': row[5],
            'produto_id': row[6],
            'qtd': row[7],
            'preco_unit': float(row[8]) if row[8] else 0,
            'desconto': float(row[9]) if row[9] else 0
        })

vendas_list = list(vendas_dict.values())
print("Vendas carregadas do MySQL: %d (com %d itens)" % (len(vendas_list), sum(len(v['itens']) for v in vendas_list)))

# Inserir no MongoDB
if vendas_list:
    vendas_col.insert_many(vendas_list)
t1 = time.time()
print("Tempo migracao MongoDB: %.2f ms" % ((t1 - t0) * 1000))

# Verificar documentos no MongoDB
n_docs = vendas_col.count_documents({})
print("N. documentos no MongoDB: %d" % n_docs)

# --- AGREGACAO: Total por loja (MongoDB) ---
t0 = time.time()
pipeline = [
    {'$group': {'_id': '$loja_id', 'total': {'$sum': '$total'}}},
    {'$sort': {'_id': 1}}
]
resultados_mongo = list(vendas_col.aggregate(pipeline))
t1 = time.time()
tempo_mongo = (t1 - t0) * 1000
print("\nAgregacao MongoDB — Total por Loja: %.2f ms" % tempo_mongo)
for r in resultados_mongo:
    print("  Loja %d: %.2f" % (r['_id'], r['total']))

n_lojas_mongo = len(resultados_mongo)
loja_top_mongo = max(resultados_mongo, key=lambda x: x['total'])
print("N. lojas no resultado: %d" % n_lojas_mongo)
print("Loja com maior total: Loja %d (%.2f)" % (loja_top_mongo['_id'], loja_top_mongo['total']))

# --- AGREGACAO: Total por loja (MySQL) ---
t0 = time.time()
cur.execute("""
    SELECT loja_id, CAST(SUM(total) AS DECIMAL(15,2)) as total
    FROM VENDA
    GROUP BY loja_id
    ORDER BY loja_id
""")
resultados_mysql = cur.fetchall()
t1 = time.time()
tempo_mysql = (t1 - t0) * 1000
print("\nQuery MySQL — Total por Loja: %.2f ms" % tempo_mysql)
for r in resultados_mysql:
    print("  Loja %d: %.2f" % (r[0], r[1]))

n_lojas_mysql = len(resultados_mysql)
loja_top_mysql = max(resultados_mysql, key=lambda x: x[1])
print("N. lojas no resultado: %d" % n_lojas_mysql)
print("Loja com maior total: Loja %d (%.2f)" % (loja_top_mysql[0], loja_top_mysql[1]))

print("\n--- COMPARACAO ---")
print("MongoDB: %.2f ms | MySQL: %.2f ms" % (tempo_mongo, tempo_mysql))
print("Mais rapido: %s" % ("MongoDB" if tempo_mongo < tempo_mysql else "MySQL"))

# ============================================================
# P3-B: MIGRAR CLIENTES COM VENDAS EMBUTIDAS
# ============================================================
print("\n" + "=" * 60)
print("P3-B: MIGRACAO CLIENTES + VENDAS -> MONGODB")
print("=" * 60)

clientes_col = db['clientes']

# Limpar colecao anterior
clientes_col.delete_many({})

# Carregar clientes com vendas
t0 = time.time()
cur.execute("""
    SELECT c.id, c.nome, c.nif, c.provincia_id, c.telefone,
           v.id, v.loja_id, v.data_venda, v.total
    FROM CLIENTE c
    LEFT JOIN VENDA v ON c.id = v.cliente_id
    ORDER BY c.id, v.id
""")

clientes_dict = {}
for row in cur:
    c_id = row[0]
    if c_id not in clientes_dict:
        clientes_dict[c_id] = {
            '_id': c_id,
            'nome': row[1],
            'nif': row[2],
            'provincia_id': row[3],
            'telefone': row[4],
            'vendas': []
        }
    if row[5]:
        clientes_dict[c_id]['vendas'].append({
            'venda_id': row[5],
            'loja_id': row[6],
            'data_venda': row[7].isoformat() if isinstance(row[7], datetime.date) else str(row[7]),
            'total': float(row[8]) if row[8] else 0
        })

clientes_list = list(clientes_dict.values())
print("Clientes carregados: %d" % len(clientes_list))

# Inserir no MongoDB
if clientes_list:
    clientes_col.insert_many(clientes_list)
t1 = time.time()
print("Tempo migracao MongoDB: %.2f ms" % ((t1 - t0) * 1000))

n_clientes_mongo = clientes_col.count_documents({})
print("N. documentos clientes no MongoDB: %d" % n_clientes_mongo)

# --- TOP 10 CLIENTES NO MONGODB ---
t0 = time.time()
top10_mongo = list(clientes_col.aggregate([
    {'$unwind': '$vendas'},
    {'$group': {'_id': '$_id', 'nome': {'$first': '$nome'}, 'total': {'$sum': '$vendas.total'}}},
    {'$sort': {'total': -1}},
    {'$limit': 10}
]))
t1 = time.time()
tempo_top_mongo = (t1 - t0) * 1000
print("\nTop 10 Clientes (MongoDB): %.2f ms" % tempo_top_mongo)
for i, r in enumerate(top10_mongo, 1):
    print("  %d. %s (total: %.2f)" % (i, r['nome'], r['total']))

# --- TOP 10 CLIENTES NO MYSQL ---
t0 = time.time()
cur.execute("""
    SELECT c.id, c.nome, CAST(SUM(v.total) AS DECIMAL(15,2)) as total_gasto
    FROM CLIENTE c
    JOIN VENDA v ON c.id = v.cliente_id
    GROUP BY c.id, c.nome
    ORDER BY total_gasto DESC
    LIMIT 10
""")
top10_mysql = cur.fetchall()
t1 = time.time()
tempo_top_mysql = (t1 - t0) * 1000
print("\nTop 10 Clientes (MySQL): %.2f ms" % tempo_top_mysql)
for i, r in enumerate(top10_mysql, 1):
    print("  %d. %s (total: %.2f)" % (i, r[1], r[2]))

print("\n--- COMPARACAO ---")
print("MongoDB: %.2f ms | MySQL: %.2f ms" % (tempo_top_mongo, tempo_top_mysql))
print("Mais rapido: %s" % ("MongoDB" if tempo_top_mongo < tempo_top_mysql else "MySQL"))

# Verificar se o top 1 coincide
if top10_mongo and top10_mysql:
    print("\nCliente top #1 MongoDB: %s" % top10_mongo[0]['nome'])
    print("Cliente top #1 MySQL:   %s" % top10_mysql[0][1])
    print("Iguais? %s" % ("S" if top10_mongo[0]['nome'] == top10_mysql[0][1] else "N"))

mysql.close()
mongo.close()
