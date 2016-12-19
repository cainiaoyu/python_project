import ConfigParser


mysql_config = ConfigParser.RawConfigParser()

mysql_config.add_section('mysql')
mysql_config.set("mysql", "host", "192.168.199.10")
mysql_config.set("mysql", "user", "test")
mysql_config.set("mysql", "passwd", "MyNewPass4!")
mysql_config.set("mysql", "db", "app_test")
mysql_config.set("mysql", "port", "3306")
mysql_config.set("mysql", "charset", "utf8")

with open("app_mysql_config.cfg", "wb") as app_config:
    mysql_config.write(app_config)

