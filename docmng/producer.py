import pika, json

params = pika.URLParameters('amqps://nafhfccg:kzeU7RMKLIuDasrfRh1_HlvSEdJelYKo@cow.rmq2.cloudamqp.com/nafhfccg')

connection = pika.BlockingConnection(params)

channel = connection.channel()

def publish(method, body):
    properties = pika.BasicProperties(method)
    channel.basic_publish(exchange='', routing_key='admin', body=json.dumps(body), properties=properties)