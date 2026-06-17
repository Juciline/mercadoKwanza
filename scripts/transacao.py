"""
Script de transação distribuída entre os 3 nós MySQL.
A ser implementado na Fase 1 do laboratório.
"""

import mysql.connector
from mysql.connector import Error

def conectar(host, porta, usuario="root", senha="root", banco="mercadokwanza"):
    try:
        conn = mysql.connector.connect(
            host=host,
            port=porta,
            user=usuario,
            password=senha,
            database=banco
        )
        return conn
    except Error as e:
        print(f"Erro ao conectar a {host}:{porta} — {e}")
        return None


def executar_venda_distribuida():
    # TODO: Implementar transação distribuída (2PC ou XA)
    # 1. Conectar aos 3 nós
    # 2. Inserir venda no nó adequado (sharding por loja)
    # 3. Garantir consistência entre os nós
    pass


if __name__ == "__main__":
    executar_venda_distribuida()
