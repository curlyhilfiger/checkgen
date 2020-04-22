from app import db
from app.models import Printer
from app import app


def get_printers(point_id):
    """
    Returns list of printer objects from db
    """

    printers = Printer.query.filter_by(point_id=point_id).all()

    return printers


def get_printer(api_key):
    """
    Return single printer object from db
    """

    printer = Printer.query.filter_by(api_key=api_key).first()

    return printer
