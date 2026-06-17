"""
Migração de dados do MySQL para MongoDB.
Executar: python scripts/migracao.py
"""
import mysql.connector, pymongo, time, datetime

MySQL_HOST = '127.0.0.1'
MySQL_PORT = 3316
MONGO_HOST = 'localhost'
MONGO_PORT = 27017

def migrar_vendas(db, cur):
    print("A migrar VENDAS + ITEM_VENDA...")
    cur.execute("""
        SELECT v.id, v.loja_id, v.cliente_id, v.data_venda, v.total,
               iv.id, iv.produto_id, iv.qtd, iv.preco_unit, iv.desconto
        FROM VENDA v LEFT JOIN ITEM_VENDA iv ON v.id = iv.venda_id
        ORDER BY v.id, iv.id
    """)
    vendas = {}
    for row in cur:
        vid = row[0]
        if vid not in vendas:
            vendas[vid] = {
                '_id': vid, 'loja_id': row[1], 'cliente_id': row[2],
                'data_venda': row[3].isoformat() if isinstance(row[3], datetime.date) else str(row[3]),
                'total': float(row[4]) if row[4] else 0, 'itens': []
            }
        if row[5]:
            vendas[vid]['itens'].append({
                'item_id': row[5], 'produto_id': row[6],
                'qtd': row[7], 'preco_unit': float(row[8]) if row[8] else 0,
                'desconto': float(row[9]) if row[9] else 0
            })
    lista = list(vendas.values())
    if lista:
        db['vendas'].delete_many({})
        db['vendas'].insert_many(lista)
    print("  %d documentos inseridos" % len(lista))

def migrar_clientes(db, cur):
    print("A migrar CLIENTES com vendas...")
    cur.execute("""
        SELECT c.id, c.nome, c.nif, c.provincia_id, c.telefone,
               v.id, v.loja_id, v.data_venda, v.total
        FROM CLIENTE c LEFT JOIN VENDA v ON c.id = v.cliente_id
        ORDER BY c.id, v.id
    """)
    clientes = {}
    for row in cur:
        cid = row[0]
        if cid not in clientes:
            clientes[cid] = {
                '_id': cid, 'nome': row[1], 'nif': row[2],
                'provincia_id': row[3], 'telefone': row[4], 'vendas': []
            }
        if row[5]:
            clientes[cid]['vendas'].append({
                'venda_id': row[5], 'loja_id': row[6],
                'data_venda': row[7].isoformat() if isinstance(row[7], datetime.date) else str(row[7]),
                'total': float(row[8]) if row[8] else 0
            })
    lista = list(clientes.values())
    if lista:
        db['clientes'].delete_many({})
        db['clientes'].insert_many(lista)
    print("  %d documentos inseridos" % len(lista))

def migrar_produtos(db, cur):
    print("A migrar PRODUTOS...")
    cur.execute("SELECT id, descricao, categoria, preco, activo FROM PRODUTO")
    produtos = []
    for row in cur:
        produtos.append({
            '_id': row[0], 'descricao': row[1], 'categoria': row[2],
            'preco': float(row[3]) if row[3] else 0, 'activo': row[4]
        })
    if produtos:
        db['produtos'].delete_many({})
        db['produtos'].insert_many(produtos)
    print("  %d documentos inseridos" % len(produtos))

def main():
    t0 = time.time()
    mysql = mysql.connector.connect(
        host=MySQL_HOST, port=MySQL_PORT,
        user='root', password='kwanza2024',
        database='mercadokwanza', autocommit=True
    )
    cur = mysql.cursor()
    mongo = pymongo.MongoClient(MONGO_HOST, MONGO_PORT)
    db = mongo['mercadokwanza']

    migrar_produtos(db, cur)
    migrar_vendas(db, cur)
    migrar_clientes(db, cur)

    mysql.close()
    mongo.close()
    t1 = time.time()
    print("\nMigracao concluida em %.2f s" % (t1 - t0))

if __name__ == '__main__':
    main()
