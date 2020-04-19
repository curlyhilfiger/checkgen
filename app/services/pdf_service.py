import os
import pypandoc

from flask import render_template

from app import app


app.app_context().push()


def pdf(data, check_type):
    
    rendered = _pdf_string(data, check_type)

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


def _pdf_string(context, check_type):

    if check_type == 'client':
        return render_template('client_check.html', context=context)
    elif check_type == 'kitchen':
        return render_template('kitchen_check.html', context=context)
    return 'error'

