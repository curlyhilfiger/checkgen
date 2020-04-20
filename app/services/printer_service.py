from app import db
from app.models import Printer

from app import app


def get_printers(point_id):

    printers = Printer.query.filter_by(point_id=point_id).all()

    return printers


def get_printer(api_key):

    printer = Printer.query.filter_by(api_key=api_key)

    return printer

