-- ============================================================
-- MercadoKwanza — Dataset para Lab #02 BDD Distribuídas
-- ISPTEC | Base de Dados II | 2025/2026
-- MySQL 8.0
-- ============================================================

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;
SET SQL_MODE = 'NO_AUTO_VALUE_ON_ZERO';

-- ─────────────────────────────────────────
-- SCHEMA
-- ─────────────────────────────────────────
DROP DATABASE IF EXISTS mercadokwanza;
CREATE DATABASE mercadokwanza
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE mercadokwanza;

-- ─────────────────────────────────────────
-- TABELAS
-- ─────────────────────────────────────────

CREATE TABLE PROVINCIA (
  id          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  nome        VARCHAR(60)  NOT NULL,
  capital     VARCHAR(60)  NOT NULL,
  populacao   INT UNSIGNED NOT NULL
) ENGINE=InnoDB;

CREATE TABLE LOJA (
  id           INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  nome         VARCHAR(100) NOT NULL,
  provincia_id INT UNSIGNED NOT NULL,
  morada       VARCHAR(200) NOT NULL,
  activa       TINYINT(1)   NOT NULL DEFAULT 1,
  INDEX idx_loja_provincia (provincia_id),
  FOREIGN KEY (provincia_id) REFERENCES PROVINCIA(id)
) ENGINE=InnoDB;

CREATE TABLE PRODUTO (
  id        INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  descricao VARCHAR(150) NOT NULL,
  categoria VARCHAR(50)  NOT NULL,
  preco     DECIMAL(10,2) NOT NULL,
  activo    TINYINT(1)   NOT NULL DEFAULT 1,
  INDEX idx_produto_categoria (categoria)
) ENGINE=InnoDB;

CREATE TABLE STOCK (
  id           INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  produto_id   INT UNSIGNED NOT NULL,
  loja_id      INT UNSIGNED NOT NULL,
  quantidade   INT UNSIGNED NOT NULL DEFAULT 0,
  atualizado_em DATETIME   NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_stock_produto (produto_id),
  INDEX idx_stock_loja    (loja_id),
  FOREIGN KEY (produto_id) REFERENCES PRODUTO(id),
  FOREIGN KEY (loja_id)    REFERENCES LOJA(id)
) ENGINE=InnoDB;

CREATE TABLE CLIENTE (
  id           INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  nome         VARCHAR(100) NOT NULL,
  nif          VARCHAR(20)  NOT NULL,
  provincia_id INT UNSIGNED NOT NULL,
  telefone     VARCHAR(20)  NOT NULL,
  activo       TINYINT(1)   NOT NULL DEFAULT 1,
  INDEX idx_cliente_provincia (provincia_id),
  INDEX idx_cliente_nif       (nif),
  FOREIGN KEY (provincia_id) REFERENCES PROVINCIA(id)
) ENGINE=InnoDB;

CREATE TABLE VENDA (
  id          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  loja_id     INT UNSIGNED NOT NULL,
  cliente_id  INT UNSIGNED NOT NULL,
  data_venda  DATETIME     NOT NULL,
  total       DECIMAL(12,2) NOT NULL DEFAULT 0,
  INDEX idx_venda_loja    (loja_id),
  INDEX idx_venda_cliente (cliente_id),
  INDEX idx_venda_data    (data_venda),
  FOREIGN KEY (loja_id)    REFERENCES LOJA(id),
  FOREIGN KEY (cliente_id) REFERENCES CLIENTE(id)
) ENGINE=InnoDB;

CREATE TABLE ITEM_VENDA (
  id          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  venda_id    INT UNSIGNED NOT NULL,
  produto_id  INT UNSIGNED NOT NULL,
  qtd         SMALLINT UNSIGNED NOT NULL,
  preco_unit  DECIMAL(10,2) NOT NULL,
  desconto    DECIMAL(5,2)  NOT NULL DEFAULT 0.00,
  INDEX idx_item_venda    (venda_id),
  INDEX idx_item_produto  (produto_id),
  FOREIGN KEY (venda_id)   REFERENCES VENDA(id),
  FOREIGN KEY (produto_id) REFERENCES PRODUTO(id)
) ENGINE=InnoDB;

-- ─────────────────────────────────────────
-- DADOS FIXOS: PROVÍNCIAS
-- ─────────────────────────────────────────
INSERT INTO PROVINCIA (nome, capital, populacao) VALUES
  ('Luanda',   'Luanda',   9292000),
  ('Benguela', 'Benguela', 2418000),
  ('Huambo',   'Huambo',   2158000);

-- ─────────────────────────────────────────
-- DADOS FIXOS: 15 LOJAS (5 por província)
-- ─────────────────────────────────────────
INSERT INTO LOJA (nome, provincia_id, morada, activa) VALUES
  -- Luanda (provincia_id = 1)
  ('MercadoKwanza Rangel',        1, 'Rua Kwame Nkrumah, 42 — Rangel, Luanda',           1),
  ('MercadoKwanza Viana',         1, 'Estrada de Viana, Km 12 — Viana, Luanda',           1),
  ('MercadoKwanza Cacuaco',       1, 'Av. do Cacuaco, 87 — Cacuaco, Luanda',              1),
  ('MercadoKwanza Talatona',      1, 'Condomínio Talatona, Loja 5 — Talatona, Luanda',    1),
  ('MercadoKwanza Sambizanga',    1, 'Rua da Missão, 15 — Sambizanga, Luanda',            1),
  -- Benguela (provincia_id = 2)
  ('MercadoKwanza Benguela Centro',2, 'Av. 4 de Fevereiro, 101 — Centro, Benguela',       1),
  ('MercadoKwanza Lobito',        2, 'Rua Serpa Pinto, 33 — Lobito, Benguela',            1),
  ('MercadoKwanza Catumbela',     2, 'Estrada Nacional 100, Km 3 — Catumbela, Benguela',  1),
  ('MercadoKwanza Balombo',       2, 'Rua Principal, 22 — Balombo, Benguela',             1),
  ('MercadoKwanza Bocoio',        2, 'Av. da Independência, 8 — Bocoio, Benguela',        1),
  -- Huambo (provincia_id = 3)
  ('MercadoKwanza Huambo Centro', 3, 'Av. Norton de Matos, 55 — Centro, Huambo',         1),
  ('MercadoKwanza Caála',         3, 'Rua da Estação, 17 — Caála, Huambo',               1),
  ('MercadoKwanza Longonjo',      3, 'Rua da Feira, 3 — Longonjo, Huambo',               1),
  ('MercadoKwanza Catchiungo',    3, 'Av. Central, 29 — Catchiungo, Huambo',             1),
  ('MercadoKwanza Mungo',         3, 'Rua do Mercado, 11 — Mungo, Huambo',               1);

-- ─────────────────────────────────────────
-- STORED PROCEDURE: 200 PRODUTOS
-- ─────────────────────────────────────────
DELIMITER $$

CREATE PROCEDURE sp_inserir_produtos()
BEGIN
  DECLARE i INT DEFAULT 1;
  DECLARE cat VARCHAR(50);
  DECLARE nome VARCHAR(150);
  DECLARE preco DECIMAL(10,2);

  -- Arrays simulados via CASE (5 categorias × 40 produtos = 200)
  WHILE i <= 200 DO
    SET cat = CASE
      WHEN i <= 40  THEN 'Alimentação'
      WHEN i <= 80  THEN 'Higiene'
      WHEN i <= 120 THEN 'Electrónica'
      WHEN i <= 160 THEN 'Vestuário'
      ELSE               'Ferragens'
    END;

    SET nome = CASE cat
      WHEN 'Alimentação' THEN
        CONCAT(
          ELT(1 + MOD(i-1,10), 'Arroz Precioso','Feijão Muamba','Massa Miramar',
              'Óleo Girassol','Sal Marinho','Açúcar Cristal','Farinha de Milho',
              'Leite Mimosa','Atum Cofaco','Sardinha Miramar'),
          ' — ', ELT(1+MOD(i-1,4),'1kg','2kg','5kg','500g'),
          ' (Ref. A', LPAD(i,3,'0'), ')'
        )
      WHEN 'Higiene' THEN
        CONCAT(
          ELT(1+MOD(i-41,10),'Sabão Protex','Champô Pantene','Pasta Colgate',
              'Desodorizante Rexona','Talco Johnson','Creme Nivea',
              'Papel Higiénico Renova','Sabonete Lux','Gel Duche Dove','Fralda Pampers'),
          ' — ', ELT(1+MOD(i-41,3),'Normal','Família','Extra'),
          ' (Ref. H', LPAD(i,3,'0'), ')'
        )
      WHEN 'Electrónica' THEN
        CONCAT(
          ELT(1+MOD(i-81,10),'Pilha AA Energizer','Pilha AAA Duracell',
              'Extensão Eléctrica','Lâmpada LED Philips','Adaptador USB',
              'Cabo HDMI','Rato USB Logitech','Teclado USB','Pen Drive 32GB',
              'Carregador Universal'),
          ' — ', ELT(1+MOD(i-81,3),'x2','x4','x8'),
          ' (Ref. E', LPAD(i,3,'0'), ')'
        )
      WHEN 'Vestuário' THEN
        CONCAT(
          ELT(1+MOD(i-121,10),'Camisola Homem','Calça Jeans','Vestido Senhora',
              'Chinelo Havaianas','Boné Adidas','Meia Adulto','T-Shirt Básica',
              'Pijama Criança','Blusa Malha','Casaco Impermeável'),
          ' — Tam. ', ELT(1+MOD(i-121,4),'P','M','G','XG'),
          ' (Ref. V', LPAD(i,3,'0'), ')'
        )
      ELSE -- Ferragens
        CONCAT(
          ELT(1+MOD(i-161,10),'Parafuso Zincado','Prego Galvanizado',
              'Fita Métrica 5m','Chave de Fendas','Martelo Carpinteiro',
              'Fio Eléctrico 2.5mm','Disjuntor 20A','Tomada Dupla',
              'Tinta Coral 18L','Massa Corrida 25kg'),
          ' — Cx ', ELT(1+MOD(i-161,3),'Pequena','Média','Grande'),
          ' (Ref. F', LPAD(i,3,'0'), ')'
        )
    END;

    SET preco = CASE cat
      WHEN 'Alimentação' THEN ROUND(500  + (RAND()*i*17),  2)
      WHEN 'Higiene'     THEN ROUND(800  + (RAND()*i*12),  2)
      WHEN 'Electrónica' THEN ROUND(1500 + (RAND()*i*85),  2)
      WHEN 'Vestuário'   THEN ROUND(2000 + (RAND()*i*55),  2)
      ELSE                    ROUND(300  + (RAND()*i*30),  2)
    END;

    INSERT INTO PRODUTO (descricao, categoria, preco, activo)
    VALUES (nome, cat, preco, 1);

    SET i = i + 1;
  END WHILE;
END$$

DELIMITER ;
CALL sp_inserir_produtos();
DROP PROCEDURE sp_inserir_produtos;

-- ─────────────────────────────────────────
-- STORED PROCEDURE: STOCK (200 × 15 = 3 000 registos)
-- ─────────────────────────────────────────
DELIMITER $$

CREATE PROCEDURE sp_inserir_stock()
BEGIN
  DECLARE p INT DEFAULT 1;
  DECLARE l INT DEFAULT 1;

  WHILE p <= 200 DO
    SET l = 1;
    WHILE l <= 15 DO
      INSERT INTO STOCK (produto_id, loja_id, quantidade, atualizado_em)
      VALUES (
        p,
        l,
        FLOOR(20 + RAND()*480),   -- entre 20 e 500 unidades
        DATE_SUB(NOW(), INTERVAL FLOOR(RAND()*90) DAY)
      );
      SET l = l + 1;
    END WHILE;
    SET p = p + 1;
  END WHILE;
END$$

DELIMITER ;
CALL sp_inserir_stock();
DROP PROCEDURE sp_inserir_stock;

-- ─────────────────────────────────────────
-- STORED PROCEDURE: 5 000 CLIENTES
-- ─────────────────────────────────────────
DELIMITER $$

CREATE PROCEDURE sp_inserir_clientes()
BEGIN
  DECLARE i       INT DEFAULT 1;
  DECLARE p_id    INT;
  DECLARE prenome VARCHAR(50);
  DECLARE apelido VARCHAR(50);
  DECLARE nif_val VARCHAR(20);
  DECLARE tel     VARCHAR(20);

  WHILE i <= 5000 DO
    -- Distribuição: 50% Luanda, 30% Benguela, 20% Huambo
    SET p_id = CASE
      WHEN i <= 2500 THEN 1
      WHEN i <= 4000 THEN 2
      ELSE                3
    END;

    SET prenome = ELT(1 + MOD(i, 30),
      'Ana','João','Maria','Pedro','Luísa','Carlos','Beatriz','Manuel',
      'Fernanda','António','Rosa','Domingos','Esperança','Augusto','Helena',
      'Francisco','Conceição','Sérgio','Filomena','Eduardo','Graça','Simão',
      'Margarida','Alfredo','Teresa','Gilberto','Eulália','Reinaldo','Fátima','Amílcar'
    );

    SET apelido = ELT(1 + MOD(i*7, 40),
      'Silva','Santos','Ferreira','Costa','Nascimento','Lopes','Martins',
      'Rodrigues','Domingos','Neto','Carvalho','Brito','Pinto','Cardoso',
      'Sousa','Mendes','Coelho','Teixeira','Baptista','Rocha','Vieira',
      'Almeida','Pereira','Gomes','Fonseca','Monteiro','Ribeiro','Dias',
      'Lima','Correia','Mota','Nunes','Ramos','Cunha','Melo','Xavier',
      'Andrade','Araújo','Campos','Borges'
    );

    SET nif_val = CONCAT(
      LPAD(MOD(i * 13 + 100000, 900000) + 100000, 9, '0'),
      'LA',
      LPAD(MOD(i, 100), 3, '0')
    );

    SET tel = CONCAT(
      ELT(1 + MOD(i, 4), '923','924','925','926'),
      LPAD(MOD(i * 97 + 100000, 1000000), 6, '0')
    );

    INSERT INTO CLIENTE (nome, nif, provincia_id, telefone, activo)
    VALUES (CONCAT(prenome, ' ', apelido), nif_val, p_id, tel, 1);

    SET i = i + 1;
  END WHILE;
END$$

DELIMITER ;
CALL sp_inserir_clientes();
DROP PROCEDURE sp_inserir_clientes;

-- ─────────────────────────────────────────
-- STORED PROCEDURE: ~30 000 VENDAS + ~80 000 ITENS
-- ─────────────────────────────────────────
DELIMITER $$

CREATE PROCEDURE sp_inserir_vendas()
BEGIN
  DECLARE i          INT DEFAULT 1;
  DECLARE v_loja     INT;
  DECLARE v_cliente  INT;
  DECLARE v_data     DATETIME;
  DECLARE v_total    DECIMAL(12,2) DEFAULT 0;
  DECLARE v_id       INT;
  DECLARE n_itens    INT;
  DECLARE j          INT;
  DECLARE v_produto  INT;
  DECLARE v_qtd      SMALLINT;
  DECLARE v_preco    DECIMAL(10,2);
  DECLARE v_desc     DECIMAL(5,2);
  DECLARE item_total DECIMAL(12,2);

  -- Pré-carregar preços para evitar SELECT dentro do loop
  CREATE TEMPORARY TABLE tmp_preco (
    id    INT UNSIGNED PRIMARY KEY,
    preco DECIMAL(10,2)
  );
  INSERT INTO tmp_preco SELECT id, preco FROM PRODUTO;

  START TRANSACTION;

  WHILE i <= 30000 DO
    SET v_loja    = 1 + MOD(i * 11 + FLOOR(RAND()*7), 15);
    SET v_cliente = 1 + MOD(i * 97 + FLOOR(RAND()*500), 5000);
    SET v_data    = DATE_ADD('2023-01-01 08:00:00',
                    INTERVAL FLOOR(RAND() * 730 * 24 * 60) MINUTE);
    SET v_total   = 0;
    SET n_itens   = 2 + MOD(i, 3);
    SET j         = 1;

    -- Calcular total antes de inserir a venda
    WHILE j <= n_itens DO
      SET v_produto = 1 + MOD(i * j * 31 + FLOOR(RAND()*50), 200);
      SET v_qtd     = 1 + MOD(i * j, 10);
      SELECT preco INTO v_preco FROM tmp_preco WHERE id = v_produto;
      SET v_desc = CASE WHEN MOD(j, 5) = 0 THEN 5.00
                        WHEN MOD(j, 3) = 0 THEN 2.50 ELSE 0.00 END;
      SET v_total = v_total + v_qtd * v_preco * (1 - v_desc / 100);
      SET j = j + 1;
    END WHILE;

    -- Inserir venda com o total correcto
    INSERT INTO VENDA (loja_id, cliente_id, data_venda, total)
    VALUES (v_loja, v_cliente, v_data, ROUND(v_total, 2));

    SET v_id = LAST_INSERT_ID();
    SET j = 1;

    -- Inserir itens
    WHILE j <= n_itens DO
      SET v_produto = 1 + MOD(i * j * 31 + FLOOR(RAND()*50), 200);
      SET v_qtd     = 1 + MOD(i * j, 10);
      SELECT preco INTO v_preco FROM tmp_preco WHERE id = v_produto;
      SET v_desc = CASE WHEN MOD(j, 5) = 0 THEN 5.00
                        WHEN MOD(j, 3) = 0 THEN 2.50 ELSE 0.00 END;

      INSERT INTO ITEM_VENDA (venda_id, produto_id, qtd, preco_unit, desconto)
      VALUES (v_id, v_produto, v_qtd, v_preco, v_desc);
      SET j = j + 1;
    END WHILE;

    SET i = i + 1;
  END WHILE;

  COMMIT;
  DROP TEMPORARY TABLE tmp_preco;
END$$

DELIMITER ;

-- Aumentar timeout para o insert massivo
SET SESSION wait_timeout          = 28800;
SET SESSION interactive_timeout   = 28800;
SET SESSION net_read_timeout      = 600;
SET SESSION net_write_timeout     = 600;

CALL sp_inserir_vendas();
DROP PROCEDURE sp_inserir_vendas;

SET FOREIGN_KEY_CHECKS = 1;

-- ─────────────────────────────────────────
-- VERIFICAÇÃO FINAL
-- ─────────────────────────────────────────
SELECT 'PROVINCIA'  AS tabela, COUNT(*) AS registos FROM PROVINCIA  UNION ALL
SELECT 'LOJA',                 COUNT(*)             FROM LOJA        UNION ALL
SELECT 'PRODUTO',              COUNT(*)             FROM PRODUTO     UNION ALL
SELECT 'STOCK',                COUNT(*)             FROM STOCK       UNION ALL
SELECT 'CLIENTE',              COUNT(*)             FROM CLIENTE     UNION ALL
SELECT 'VENDA',                COUNT(*)             FROM VENDA       UNION ALL
SELECT 'ITEM_VENDA',           COUNT(*)             FROM ITEM_VENDA;

-- ─────────────────────────────────────────
-- FIM DO SCRIPT — MercadoKwanza v1.0
-- ─────────────────────────────────────
