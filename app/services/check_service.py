from app.models import Check
from app import app


def get_checks(printer_id):
    """
    Returns list of check objects from db
    """

    checks = Check.query.filter_by(
        printer_id=printer_id, status='rendered'
    ).all()

    return checks


def get_check(id, printer_id):
    """
    Return single check object from db
    """

    check = Check.query.filter_by(id=id, printer_id=printer_id).first()

    return check


def create_check(data, printer, pdf_file):
    """
    Creates checks object and return it
    """

    check = Check(
        order_id=data['id'],
        printer=printer,
        check_type=printer.check_type,
        order=data,
        status='rendered',
        pdf_file=pdf_file
    )

    return check


def is_created(order_id):
    """
    Check object was created or not
    """

    check = Check.query.filter_by(order_id=order_id).first()

    if not check:
        return False

    return True
