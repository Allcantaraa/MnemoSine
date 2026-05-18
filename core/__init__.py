import sys

# Truque para ambiente local no Windows: 
# Usa o PyMySQL como "dublê" do mysqlclient para evitar dor de cabeça com compilação C e SSL
if sys.platform == 'win32':
    import pymysql
    pymysql.install_as_MySQLdb()
    
    # Fazendo o Django acreditar que estamos usando a versão mais recente do mysqlclient
    import MySQLdb
    MySQLdb.version_info = (2, 2, 4, 'final', 0)