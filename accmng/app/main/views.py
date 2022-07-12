from flask import render_template, flash, redirect, url_for
from flask_login import current_user
from . import main
from ..models import User, Document, ConfirmationStatus, datetime
from .forms import DocumentForm
from .. import db


@main.route('/')
def index():
    documents = Document.query.order_by(Document.timestamp.desc()).all()
    return render_template('index.html', documents=documents)


@main.route('/document_edit/<int:id>', methods=['GET', 'POST'])
def document_edit(id):
    document = Document.query.get_or_404(id)
    
    form = DocumentForm()
    if form.validate_on_submit():
        for itm in dir(form):
            try:
                document[itm] = form[itm].data
            except:
                pass
        document.confirmation_status = ConfirmationStatus[form.confirmation_status.data]
        document.confirmation_date = datetime.utcnow()
        document.responsible_id = current_user.id
        db.session.commit()
        
        flash('The document has been updated.')
        
        documents = Document.query.order_by(Document.timestamp.desc()).all()
        return render_template('index.html', documents=documents)
    form.code.data = document.code
    form.description.data = document.description
    form.timestamp.data = document.timestamp
    form.body.data = document.body
    form.sum.data = document.sum
    form.confirmation_status.data = document.confirmation_status.name
    return render_template('document_edit.html', form=form)