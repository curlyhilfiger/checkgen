from app import db


class Printer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    api_key = db.Column(db.String(30), unique=True)
    check_type = db.Column(db.String(30))
    point_id = db.Column(db.Integer)
    checks = db.relationship('Check', backref='printer')


class Check(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, nullable=False)
    printer_id = db.Column(db.Integer, db.ForeignKey('printer.id'))
    check_type = db.Column(db.String(30))
    order = db.Column(db.JSON())
    status = db.Column(db.String(30), default='new')
    pdf_file = db.Column(db.String(256))
