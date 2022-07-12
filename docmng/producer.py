import pika, json

creds_broker = pika.PlainCredentials("queue_user", "Q123456q")
conn_params = pika.ConnectionParameters(host="127.0.0.1", port=5672,
                                        virtual_host = "/",
                                        credentials = creds_broker)

connection = pika.BlockingConnection(conn_params)

channel = connection.channel()

def publish(method, body):
    properties = pika.BasicProperties(method)
    channel.basic_publish(exchange='docaccmng_main',
                          routing_key='accmng',
                          body=json.dumps(body),
                          properties=properties)