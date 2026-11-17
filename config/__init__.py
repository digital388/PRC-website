"""
Allow PyMySQL as a drop-in for MySQLdb.

cPanel environments sometimes fail to compile the C-extension `mysqlclient`.
PyMySQL is pure Python and needs no compiler. Django uses whichever is present:
we try PyMySQL first and fall back to nothing (settings then require mysqlclient).
"""
try:
    import pymysql

    pymysql.install_as_MySQLdb()
except ImportError:
    pass
