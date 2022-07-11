from flask import render_template, flash, redirect, url_for
from . import main
from ..models import User, Document, ConfirmationStatus
from .forms import DocumentForm
from .. import db


@main.route('/')
def index():
    documents = Document.query.order_by(Document.timestamp.desc()).all()
    return render_template('index.html', documents=documents)


@main.route('/document_edit/<int:id>')
def document_edit(id):
    document = Document.query.get_or_404(id)
    
    form = DocumentForm()
    if form.validate_on_submit():
        document.body = form.body.data
        db.session.add(document)
        db.session.commit()
        flash('The document has been updated.')
        # return redirect(url_for('.post', id=post.id))
        documents = Document.query.order_by(Document.timestamp.desc()).all()
        return render_template('index.html', documents=documents)
    form.code.data = document.code
    form.description.data = document.description
    form.timestamp.data = document.timestamp
    form.body.data = document.body
    form.sum.data = document.sum
    # form.confirmation_status.data = ConfirmationStatus[document.confirmation_status]
    return render_template('document_edit.html', form=form)