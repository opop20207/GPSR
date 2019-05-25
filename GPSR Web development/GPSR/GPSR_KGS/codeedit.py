from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

from flask.ext import admin, wtf
from flask.ext.admin.contrib import sqlamodel

app = Flask(__name__)
app.config['SECRET_KEY'] = '123456790'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.sqlite'
db = SQLAlchemy(app)


class CKTextAreaWidget(wtf.TextArea):
    def __call__(self, field, **kwargs):
        kwargs.setdefault('class_', 'ckeditor')
        return super(CKTextAreaWidget, self).__call__(field, **kwargs)


class CKTextAreaField(wtf.TextAreaField):
    widget = CKTextAreaWidget()


class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.UnicodeText)


class TestAdmin(sqlamodel.ModelView):
    form_overrides = dict(text=CKTextAreaField)

    create_template = 'edit.html'
    edit_template = 'edit.html'


if __name__ == '__main__':
    admin = admin.Admin(app)
    admin.add_view(TestAdmin(Test, db.session))
    db.create_all()
    app.debug = True
    app.run('0.0.0.0', 8000)