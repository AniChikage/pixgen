

from helper.mysql import MySQLConnector

# mysql_connector = MySQLConnector()
# mysql_connector.connect()
email = "8772222"
out_trade_no = "fff"
order_created_timestamp = "dddddd"

# query = f"insert into orders (email, out_trade_no, total_amount, \
#                 trade_status, trade_no, gmt_create, gmt_payment, create_time) values \
#                 ('{email}', '{out_trade_no}', '', '', '', '', '', '{order_created_timestamp}')"
# print(f"create order [query]: {query}")
# result = mysql_connector.execute_query(query)
# mysql_connector.disconnect()

query = "INSERT INTO orders (email, out_trade_no, total_amount, trade_status, trade_no, gmt_create, gmt_payment, create_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
values = (email, out_trade_no, None, None, None, None, None, order_created_timestamp)

mysql_connector = MySQLConnector()
mysql_connector.connect()
result = mysql_connector.execute_query(query, values)
mysql_connector.disconnect()