import os
from flask_migrate import Migrate
from app import create_app, db
from app.models import User, Document, ConfirmationStatus

conf_name = os.getenv('FLASK_CONFIG') or 'default'
print(f'{conf_name=}')
app = create_app(conf_name)
migrate = Migrate(app, db)


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Document=Document)


if __name__ == '__main__':
    app.run(debug=True, use_debugger=False, use_reloader=False)