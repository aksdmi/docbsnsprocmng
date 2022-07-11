import pika, json
from accmng import Document, db, app
from datetime import datetime

app_ctx = app.app_context()
app_ctx.push()

creds_broker = pika.PlainCredentials("queue_user", "Q123456q")
conn_params = pika.ConnectionParameters(host="172.17.0.1", port=5672,
                                        virtual_host = "/",
                                        credentials = creds_broker)

connection = pika.BlockingConnection(conn_params)

channel = connection.channel()

print('Create channel')

def callback(ch, method, properties, body):
    print('Receive in accmng')
    data = json.loads(body)
    print(properties.content_type)
    print(data)
    if properties.content_type == 'document_created':
        document = Document(idrref=data['_idrref'],
                            code=data['_code'],
                            description=data['_description'],
                            body=data['_content'],
                            timestamp=datetime.strptime(data['_create_date'], '%d.%m.%Y'),
                            sum=data['_sum'],
                            confirmation_status='Undefined')
                
        db.session.add(document)
        db.session.commit()
        print('Document created')
    elif properties.content_type == 'document_updated':
        document = Document.query.filter_by(idrref=data['_idrref']).first()
        if document is None:
            document = Document(idrref=data['_idrref'],
                            code=data['_code'],
                            description=data['_description'],
                            body=data['_content'],
                            timestamp=datetime.strptime(data['_create_date'], '%d.%m.%Y'),
                            sum=data['_sum'])
            
            db.session.add(document)
            db.session.commit()
            print('Document created')
        else:
            product = Document.query.get(data['_idrref'])
            product.code=data['_code']
            product.description=data['_description']
            product.body=data['_content']
            product.timestamp=datetime.strptime(data['_create_date'], '%d.%m.%Y')
            product.sum=data['_sum']
            product.confirmation_status='Undefined'

            db.session.commit()
            print('Document updated')


channel.basic_consume(queue='accmng', on_message_callback=callback, auto_ack=True)

print('Started consuming')

channel.start_consuming()

channel.close()