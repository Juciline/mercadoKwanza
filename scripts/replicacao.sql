-- Configuração da replicação MySQL (master → slave1, slave2)
-- Executar no master após inicialização

-- No master:
CREATE USER IF NOT EXISTS 'replicador'@'%' IDENTIFIED BY 'replicador';
GRANT REPLICATION SLAVE ON *.* TO 'replicador'@'%';
FLUSH PRIVILEGES;

-- Obter dados do binlog:
-- SHOW MASTER STATUS;

-- Em cada slave:
-- CHANGE MASTER TO
--   MASTER_HOST='mysql-master',
--   MASTER_USER='replicador',
--   MASTER_PASSWORD='replicador',
--   MASTER_LOG_FILE='mysql-bin.000001',
--   MASTER_LOG_POS=xxx;
-- START SLAVE;
-- SHOW SLAVE STATUS\G
