import mysql.connector

conexao = mysql.connector.connect(
    host="localhost",
    user="root",
    password="senai"
)


cursor = conexao.cursor()

cursor.execute("CREATE DATABASE IF NOT EXISTS pwbe_escola")

cursor.execute("USE pwbe_escola")

cursor.execute("CREATE TABLE IF NOT EXISTS dados_login (id_professor INT AUTO_INCREMENT PRIMARY KEY, nome VARCHAR(255), login VARCHAR(255), senha VARCHAR(255))")

cursor.execute("CREATE TABLE IF NOT EXISTS turmas (id_turma INT AUTO_INCREMENT PRIMARY KEY, descricao VARCHAR(255))")

cursor.execute("CREATE TABLE IF NOT EXISTS atividades (id_atividade INT AUTO_INCREMENT PRIMARY KEY, descricao VARCHAR(255))")

cursor.execute("CREATE TABLE IF NOT EXISTS turmas_professor (id INT AUTO_INCREMENT PRIMARY KEY, id_professor INT, id_turma INT, FOREIGN KEY (id_professor) "
               "REFERENCES dados_login(id_professor), FOREIGN KEY (id_turma) REFERENCES turmas(id_turma))")

cursor.execute("CREATE TABLE IF NOT EXISTS atividades_turma (id INT AUTO_INCREMENT PRIMARY KEY, id_turma INT, id_atividade INT, FOREIGN KEY (id_turma) "
               "REFERENCES turmas(id_turma), FOREIGN KEY (id_atividade) REFERENCES atividades(id_atividade))")


cursor.close()
conexao.close()

print("Banco de dados e tabelas criados com sucesso.")