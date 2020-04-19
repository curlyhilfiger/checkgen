from flask import Flask
from flask_sqlalchemy import SQLAlchemy

import pypandoc, redis
from rq import Queue
import os


app = Flask(__name__)


r = redis.Redis()
q = Queue(connection=r)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:12345@localhost/test_check'
app.config['DEBUG'] = True
app.config['SESSION_COOKIE_SECURE'] = False
app.config['MEDIA_FOLDER'] = '/mnt/c/wsl/projects/checkge_api/media/pdf'

db = SQLAlchemy(app)

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


from flask import jsonify, request, render_template, send_file


@app.route('/create_checks', methods=['POST'])
def create_checks():
    if request.is_json:
        data = request.get_json()

        if is_created(data['id']):
            return jsonify({'error': 'Для данного заказа уже созданы чеки'}), 400

        printers = Printer.query.filter_by(point_id=data['point_id']).all()
        
        if printers:
            
            job = q.enqueue(background_check, data=data, printers=printers)
            print(f'Task ({job.id}) added to queue at {job.enqueued_at}')


            return jsonify({'ok':'Чеки успешно созданы'})

        return jsonify({'msg':'Для данной точки не настроено ни одного принтера'})

    return jsonify({'msg': 'no json recivied'})


@app.route('/new_checks/<api_key>', methods=["GET"])
def new_checks(api_key):

    printer = Printer.query.filter_by(api_key=api_key).first()

    if printer:
        checks = Check.query.filter_by(printer_id=printer.id, status='rendered').all()

        print(checks)

        output = []

        for check in checks:

            check_data = {}
            check_data['id'] = check.id
            output.append(check_data)

        return jsonify({'msg': output})
    
    return jsonify({'error': 'Ошибка авторизации'}), 401


@app.route('/check/<api_key>/<id>')
def check(api_key, id):

    printer = Printer.query.filter_by(api_key=api_key).first()

    if printer:

        check = Check.query.filter_by(id=id, printer=printer).first()

        if check:

            filename = check.pdf_file

            check.status = 'printed'
            db.session.commit()

            
            return send_file(
                filename_or_fp=filename,
                mimetype='application/pdf',
                as_attachment=True
            )

        
        else:
            return jsonify({'error':'Данного чека не существует или файл не создан'}), 400

    else:
        return jsonify({'error': 'Ошибка авторизации'}), 401
    



def background_check(data, printers):
    
    for printer in printers:

        pdf_file = pdf(data, str(printer.check_type))

        print(pdf_file)

        check = Check(
            order_id=data['id'],
            printer=printer,
            check_type=printer.check_type,
            order=data,
            status='rendered',
            pdf_file=pdf_file
        )
        db.session.add(check)
    
    db.session.commit()
    print('checks added')


def pdf(data, check_type):
    
    rendered = generate_pdf(data, check_type)

    document_id = data['id']
    check_type = check_type

    outputfile = os.path.join(app.config['MEDIA_FOLDER'], f'{document_id}_{check_type}.pdf')

    pdf = pypandoc.convert_text(
        rendered, 
        'pdf', 
        format='html', 
        outputfile=outputfile, 
        extra_args=['--latex-engine=xelatex', '-V', 'mainfont="FreeSerifBold"']
    )

    return outputfile


def generate_pdf(context, check_type):

    print(context)
    print(check_type)
    print(app)

    app.app_context().push()

    if check_type == 'client':
        return render_template('client_check.html', context=context)
    elif check_type == 'kitchen':
        return render_template('kitchen_check.html', context=context)
    return 'error'


def is_created(order_id):

    check = Check.query.filter_by(order_id=order_id).first()

    if not check:
        return False

    return True
