import mysql.connector

def conectar():
    return mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = "senai",
        database= "pwbe_escola"
    )

