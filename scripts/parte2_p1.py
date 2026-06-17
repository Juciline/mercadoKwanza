"""
Parte 2 — P1-A: Replication delay test (COUNT PRODUTO + INSERTs)
       P1-B: COUNT CLIENTE + FRAGMENTATION
"""
import mysql.connector, time

def conectar(porta):
    return mysql.connector.connect(
        host='127.0.0.1', port=porta,
        user='root', password='kwanza2024',
        database='mercadokwanza', autocommit=True
    )

print("=" * 60)
print("P1-A: REPLICACAO — COUNT PRODUTO")
print("=" * 60)

c_l = conectar(3316); c_b = conectar(3307)
cur_l = c_l.cursor(); cur_b = c_b.cursor()

# ANTES
cur_l.execute('SELECT COUNT(*) FROM PRODUTO')
p_l_antes = cur_l.fetchone()[0]
cur_b.execute('SELECT COUNT(*) FROM PRODUTO')
p_b_antes = cur_b.fetchone()[0]
print(f"COUNT PRODUTO Luanda (antes): {p_l_antes}")
print(f"COUNT PRODUTO Benguela (antes): {p_b_antes}")

# INSERT 5 novos produtos
novos_prod = [
    ('Agua Luso 1.5L', 'Bebidas', 200.00),
    ('Manteiga Mimosa 250g', 'Laticinios', 550.00),
    ('Farinha Trigo 1kg', 'Cereais', 380.00),
    ('Detergente Omo 500g', 'Limpeza', 750.00),
    ('Sabonete Dove 90g', 'Higiene', 180.00),
]
for d, c, p in novos_prod:
    cur_l.execute('INSERT INTO PRODUTO (descricao, categoria, preco) VALUES (%s,%s,%s)', (d, c, p))
print(f"Inseridos {len(novos_prod)} produtos em Luanda")

# IMEDIATAMENTE
cur_b.execute('SELECT COUNT(*) FROM PRODUTO')
p_b_imediato = cur_b.fetchone()[0]
print(f"COUNT PRODUTO Benguela (imediatamente): {p_b_imediato}")

# Seconds_Behind
cur_b.execute('SHOW SLAVE STATUS')
row = cur_b.fetchone()
desc = [d[0] for d in cur_b.description]
sbm = row[desc.index('Seconds_Behind_Master')] if row else None
print(f"Seconds_Behind_Master (imediatamente): {sbm}")

# APOS 5 SEGUNDOS
time.sleep(5)
cur_b.execute('SELECT COUNT(*) FROM PRODUTO')
p_b_apos5 = cur_b.fetchone()[0]
print(f"COUNT PRODUTO Benguela (apos 5s): {p_b_apos5}")

# Max Seconds_Behind
max_sbm = 0
for _ in range(5):
    cur_b.execute('SHOW SLAVE STATUS')
    row = cur_b.fetchone()
    if row:
        s = row[desc.index('Seconds_Behind_Master')]
        if s is not None and s > max_sbm:
            max_sbm = s
    time.sleep(1)
print(f"Seconds_Behind_Master maximo: {max_sbm}")

# Stock total fragmentos
cur_l.execute('SELECT COALESCE(SUM(quantidade),0) FROM STOCK WHERE loja_id BETWEEN 1 AND 5')
stock_l = cur_l.fetchone()[0]
cur_l.execute('SELECT COALESCE(SUM(quantidade),0) FROM STOCK WHERE loja_id BETWEEN 6 AND 10')
stock_b = cur_l.fetchone()[0]
print(f"Stock total fragmento Luanda: {stock_l}")
print(f"Stock total fragmento Benguela: {stock_b}")

c_l.close(); c_b.close()

print()
print("=" * 60)
print("P1-B: REPLICACAO — COUNT CLIENTE + FRAGMENTACAO")
print("=" * 60)

c_l = conectar(3316); c_b = conectar(3307)
cur_l = c_l.cursor(); cur_b = c_b.cursor()

# ANTES
cur_l.execute('SELECT COUNT(*) FROM CLIENTE')
cl_l_antes = cur_l.fetchone()[0]
cur_b.execute('SELECT COUNT(*) FROM CLIENTE')
cl_b_antes = cur_b.fetchone()[0]
print(f"COUNT CLIENTE Luanda (antes): {cl_l_antes}")
print(f"COUNT CLIENTE Benguela (antes): {cl_b_antes}")

# INSERT 3 novos clientes
novos_cli = [
    ('Joaquim Manuel', '123456789', 1, '923456789'),
    ('Ana Paula Santos', '987654321', 2, '912345678'),
    ('Carlos Fragoso', '456789123', 3, '934567891'),
]
for nome, nif, prov, tel in novos_cli:
    cur_l.execute('INSERT INTO CLIENTE (nome, nif, provincia_id, telefone) VALUES (%s,%s,%s,%s)',
                  (nome, nif, prov, tel))
print(f"Inseridos {len(novos_cli)} clientes em Luanda")

# Luanda after INSERT
cur_l.execute('SELECT COUNT(*) FROM CLIENTE')
cl_l_apos = cur_l.fetchone()[0]
print(f"COUNT CLIENTE Luanda (apos INSERT): {cl_l_apos}")

# Benguela after INSERT
time.sleep(0.5)
cur_b.execute('SELECT COUNT(*) FROM CLIENTE')
cl_b_imed = cur_b.fetchone()[0]
print(f"COUNT CLIENTE Benguela (imediatamente): {cl_b_imed}")

# 5 seconds
time.sleep(5)
cur_b.execute('SELECT COUNT(*) FROM CLIENTE')
cl_b_apos5 = cur_b.fetchone()[0]
print(f"COUNT CLIENTE Benguela (apos 5s): {cl_b_apos5}")

# Seconds_Behind max
max_sbm = 0
cur_b.execute('SHOW SLAVE STATUS')
desc = [d[0] for d in cur_b.description]
for _ in range(5):
    cur_b.execute('SHOW SLAVE STATUS')
    row = cur_b.fetchone()
    if row:
        s = row[desc.index('Seconds_Behind_Master')]
        if s is not None and s > max_sbm:
            max_sbm = s
    time.sleep(1)
print(f"Seconds_Behind_Master maximo: {max_sbm}")

# SUM fragments = total?
cur_l.execute("""SELECT CASE WHEN loja_id BETWEEN 1 AND 5 THEN 'Luanda'
                             WHEN loja_id BETWEEN 6 AND 10 THEN 'Benguela'
                             ELSE 'Huambo' END as frag,
                        COUNT(*) as total
                 FROM VENDA GROUP BY frag ORDER BY frag""")
frags = cur_l.fetchall()
soma = sum(r[1] for r in frags)
cur_l.execute('SELECT COUNT(*) FROM VENDA')
total_v = cur_l.fetchone()[0]
print(f"Fragmentos: Luanda={frags[0][1]}, Benguela={frags[1][1]}, Huambo={frags[2][1]}")
print(f"Soma fragmentos={soma}, Total VENDA={total_v}")
print(f"Soma = total geral? {'S' if soma == total_v else 'N'}")

# Provincia com maior faturamento medio por cliente
cur_l.execute("""
    SELECT p.nome, AVG(v.total) as media
    FROM VENDA v
    JOIN LOJA l ON v.loja_id = l.id
    JOIN PROVINCIA p ON l.provincia_id = p.id
    GROUP BY p.id, p.nome
    ORDER BY media DESC
    LIMIT 1
""")
r = cur_l.fetchone()
print(f"Provincia com maior faturamento medio: {r[0]} (media={r[1]:.2f})")

c_l.close(); c_b.close()
