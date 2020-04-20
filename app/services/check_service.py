from app.models import Check

from app import app


def get_checks(printer_id):

    checks = Check.query.filter_by(printer_id=printer_id)

    return checks


def get_check(id):

    check = Check.query.filter_by(id=id)

    return check


def create_check(data, printer, pdf_file):

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

    check = Check.query.filter_by(order_id=order_id).first()

    if not check:
        return False

    return True
