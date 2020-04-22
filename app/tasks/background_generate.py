from app.services import printer_service, pdf_service, check_service
from app import db
from app import app


def generate(data):

    printers = printer_service.get_printers(data['point_id'])

    for printer in printers:

        pdf_file = pdf_service.pdf(data, printer.check_type)

        check = check_service.create_check(data, printer, pdf_file)

        db.session.add(check)
    
    db.session.commit()

    print('checks added')
