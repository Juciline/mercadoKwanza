"""
Parte 2 — P2-A: Distributed Transaction (Stock Benguela)
       P2-B: Distributed Transaction (Transfer Huambo -> Benguela)
"""
import mysql.connector, datetime

def log(msg):
    ts = datetime.datetime.now().strftime('%H:%M:%S.%f')[:12]
    print('[%s] %s' % (ts, msg))

def conectar(porta):
    return mysql.connector.connect(
        host='127.0.0.1', port=porta,
        user='root', password='kwanza2024',
        database='mercadokwanza',
        autocommit=False
    )

PRODUTO_ID = 5
LOJA_BENGUELA = 6
LOJA_LUANDA = 1
CLIENTE_ID = 42
QTDE = 10

print("=" * 60)
print("P2-A: TRANSACAO DISTRIBUIDA — COMPRA EM BENGUELA")
print("=" * 60)

no_luanda = conectar(3316)
no_benguela = conectar(3307)

cur_l = no_luanda.cursor()
cur_b = no_benguela.cursor()

try:
    # Stock ANTES em Benguela
    cur_b.execute('SELECT quantidade FROM STOCK WHERE produto_id=%s AND loja_id=%s FOR UPDATE',
                  (PRODUTO_ID, LOJA_BENGUELA))
    stock_antes = cur_b.fetchone()[0]
    log('Stock Benguela ANTES: %d' % stock_antes)

    # VENDAS ANTES em Luanda
    cur_l.execute('SELECT COUNT(*) FROM VENDA')
    vendas_antes = cur_l.fetchone()[0]
    log('Vendas Luanda ANTES: %d' % vendas_antes)

    # Verificar stock suficiente
    if stock_antes < QTDE:
        raise Exception('Stock insuficiente')

    # Decrementar stock em Benguela
    cur_b.execute('UPDATE STOCK SET quantidade=quantidade-%s WHERE produto_id=%s AND loja_id=%s',
                  (QTDE, PRODUTO_ID, LOJA_BENGUELA))
    log('Stock Benguela decrementado: -%d' % QTDE)

    # Inserir VENDA em Luanda
    cur_l.execute('INSERT INTO VENDA (loja_id, cliente_id, data_venda, total) VALUES (%s,%s,NOW(),%s)',
                  (LOJA_LUANDA, CLIENTE_ID, QTDE * 1500))
    venda_id = cur_l.lastrowid
    cur_l.execute('INSERT INTO ITEM_VENDA (venda_id, produto_id, qtd, preco_unit, desconto) VALUES (%s,%s,%s,%s,%s)',
                  (venda_id, PRODUTO_ID, QTDE, 1500, 0.0))
    log('Venda registada em Luanda: id=%d' % venda_id)

    # COMMIT em ambos
    no_benguela.commit()
    no_luanda.commit()
    log('COMMIT efectuado em ambos os nos')

    # Verificar stock APOS
    cur_b.execute('SELECT quantidade FROM STOCK WHERE produto_id=%s AND loja_id=%s',
                  (PRODUTO_ID, LOJA_BENGUELA))
    stock_apos = cur_b.fetchone()[0]
    log('Stock Benguela APOS transacao OK: %d' % stock_apos)

    cur_l.execute('SELECT COUNT(*) FROM VENDA')
    vendas_apos = cur_l.fetchone()[0]
    log('Vendas Luanda APOS transacao OK: %d' % vendas_apos)

except Exception as e:
    no_benguela.rollback()
    no_luanda.rollback()
    log('ROLLBACK efectuado. Motivo: %s' % e)

finally:
    cur_l.close()
    cur_b.close()
    no_luanda.close()
    no_benguela.close()

# Now P2-A part 2: Force error and check ROLLBACK
print()
print("--- P2-A: TESTE COM ERRO FORCADO ---")

no_luanda = conectar(3316)
no_benguela = conectar(3307)
cur_l = no_luanda.cursor()
cur_b = no_benguela.cursor()

try:
    cur_b.execute('SELECT quantidade FROM STOCK WHERE produto_id=%s AND loja_id=%s FOR UPDATE',
                  (PRODUTO_ID, LOJA_BENGUELA))
    stock_antes2 = cur_b.fetchone()[0]
    log('Stock Benguela ANTES (2): %d' % stock_antes2)

    cur_l.execute('SELECT COUNT(*) FROM VENDA')
    vendas_antes2 = cur_l.fetchone()[0]
    log('Vendas Luanda ANTES (2): %d' % vendas_antes2)

    cur_b.execute('UPDATE STOCK SET quantidade=quantidade-%s WHERE produto_id=%s AND loja_id=%s',
                  (QTDE, PRODUTO_ID, LOJA_BENGUELA))
    log('Stock decrementado, a forcar erro...')

    cur_l.execute('INSERT INTO VENDA (loja_id, cliente_id, data_venda, total) VALUES (%s,%s,NOW(),%s)',
                  (LOJA_LUANDA, CLIENTE_ID, QTDE * 1500))
    venda_id2 = cur_l.lastrowid
    cur_l.execute('INSERT INTO ITEM_VENDA (venda_id, produto_id, qtd, preco_unit, desconto) VALUES (%s,%s,%s,%s,%s)',
                  (venda_id2, PRODUTO_ID, QTDE, 1500, 0.0))

    raise Exception('Erro forçado para testar ROLLBACK')

except Exception as e:
    no_benguela.rollback()
    no_luanda.rollback()
    log('ROLLBACK efectuado. Motivo: %s' % e)

    cur_b.execute('SELECT quantidade FROM STOCK WHERE produto_id=%s AND loja_id=%s',
                  (PRODUTO_ID, LOJA_BENGUELA))
    stock_apos_roll = cur_b.fetchone()[0]
    log('Stock Benguela APOS ROLLBACK: %d (igual ao antes? %s)' % (
        stock_apos_roll, 'Sim' if stock_apos_roll == stock_antes2 else 'Nao'))

    cur_l.execute('SELECT COUNT(*) FROM VENDA')
    vendas_apos_roll = cur_l.fetchone()[0]
    log('Vendas Luanda APOS ROLLBACK: %d (igual ao antes? %s)' % (
        vendas_apos_roll, 'Sim' if vendas_apos_roll == vendas_antes2 else 'Nao'))

finally:
    cur_l.close()
    cur_b.close()
    no_luanda.close()
    no_benguela.close()

print()
print("=" * 60)
print("P2-B: TRANSFERENCIA ENTRE HUAMBO E BENGUELA")
print("=" * 60)

# P2-B: Transfer Huambo -> Benguela (successful)
no_huambo = conectar(3308)
no_benguela = conectar(3307)
cur_h = no_huambo.cursor()
cur_b = no_benguela.cursor()

QTDE_TRANSF = 20  # quantidade suficiente

try:
    cur_h.execute('SELECT quantidade FROM STOCK WHERE produto_id=%s AND loja_id=%s FOR UPDATE',
                  (PRODUTO_ID, 11))
    stock_h_antes = cur_h.fetchone()[0]
    log('Stock Huambo ANTES: %d' % stock_h_antes)

    cur_b.execute('SELECT quantidade FROM STOCK WHERE produto_id=%s AND loja_id=%s FOR UPDATE',
                  (PRODUTO_ID, LOJA_BENGUELA))
    stock_b_antes_transf = cur_b.fetchone()[0]
    log('Stock Benguela ANTES: %d' % stock_b_antes_transf)

    if stock_h_antes < QTDE_TRANSF:
        raise Exception('Stock insuficiente em Huambo')

    cur_h.execute('UPDATE STOCK SET quantidade=quantidade-%s WHERE produto_id=%s AND loja_id=%s',
                  (QTDE_TRANSF, PRODUTO_ID, 11))
    cur_b.execute('UPDATE STOCK SET quantidade=quantidade+%s WHERE produto_id=%s AND loja_id=%s',
                  (QTDE_TRANSF, PRODUTO_ID, LOJA_BENGUELA))

    no_huambo.commit()
    no_benguela.commit()
    log('Transferencia OK: Huambo -%d, Benguela +%d' % (QTDE_TRANSF, QTDE_TRANSF))

    cur_h.execute('SELECT quantidade FROM STOCK WHERE produto_id=%s AND loja_id=%s',
                  (PRODUTO_ID, 11))
    stock_h_apos = cur_h.fetchone()[0]
    log('Stock Huambo APOS transferencia: %d' % stock_h_apos)

    cur_b.execute('SELECT quantidade FROM STOCK WHERE produto_id=%s AND loja_id=%s',
                  (PRODUTO_ID, LOJA_BENGUELA))
    stock_b_apos = cur_b.fetchone()[0]
    log('Stock Benguela APOS transferencia: %d' % stock_b_apos)

except Exception as e:
    no_huambo.rollback()
    no_benguela.rollback()
    log('ROLLBACK. Motivo: %s' % e)

finally:
    cur_h.close()
    cur_b.close()
    no_huambo.close()
    no_benguela.close()

print()
print("--- P2-B: TESTE STOCK INSUFICIENTE ---")

no_huambo = conectar(3308)
no_benguela = conectar(3307)
cur_h = no_huambo.cursor()
cur_b = no_benguela.cursor()

QTDE_EXCESSO = 9999  # valor que excede qualquer stock

try:
    cur_h.execute('SELECT quantidade FROM STOCK WHERE produto_id=%s AND loja_id=%s FOR UPDATE',
                  (PRODUTO_ID, 11))
    stock_h_antes2 = cur_h.fetchone()[0]
    log('Stock Huambo ANTES (teste insuficiente): %d' % stock_h_antes2)

    cur_b.execute('SELECT quantidade FROM STOCK WHERE produto_id=%s AND loja_id=%s FOR UPDATE',
                  (PRODUTO_ID, LOJA_BENGUELA))
    stock_b_antes2 = cur_b.fetchone()[0]
    log('Stock Benguela ANTES (teste insuficiente): %d' % stock_b_antes2)

    if stock_h_antes2 < QTDE_EXCESSO:
        raise Exception('Stock insuficiente em Huambo para transferir %d' % QTDE_EXCESSO)

except Exception as e:
    no_huambo.rollback()
    no_benguela.rollback()
    log('ROLLBACK efectuado. Motivo: %s' % e)

    # Verificar se voltou ao inicial
    cur_h.execute('SELECT quantidade FROM STOCK WHERE produto_id=%s AND loja_id=%s',
                  (PRODUTO_ID, 11))
    stock_h_roll = cur_h.fetchone()[0]
    log('Stock Huambo APOS ROLLBACK: %d (igual ao antes? %s)' % (
        stock_h_roll, 'Sim' if stock_h_roll == stock_h_antes2 else 'Nao'))

    cur_b.execute('SELECT quantidade FROM STOCK WHERE produto_id=%s AND loja_id=%s',
                  (PRODUTO_ID, LOJA_BENGUELA))
    stock_b_roll = cur_b.fetchone()[0]
    log('Stock Benguela APOS ROLLBACK: %d (igual ao antes? %s)' % (
        stock_b_roll, 'Sim' if stock_b_roll == stock_b_antes2 else 'Nao'))

finally:
    cur_h.close()
    cur_b.close()
    no_huambo.close()
    no_benguela.close()
