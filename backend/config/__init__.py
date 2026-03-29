"""使用 PyMySQL 作为 MySQL 驱动（与 django.db.backends.mysql 兼容）。"""
try:
    import pymysql

    pymysql.install_as_MySQLdb()
except ImportError:
    pass
