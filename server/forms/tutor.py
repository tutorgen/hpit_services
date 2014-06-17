from wtforms import form, fields, validators

class TutorForm(form.Form):
    name = fields.StringField('Tutor Name', validators=[validators.input_required()])
    description = fields.StringField('Tutor Description', validators=[validators.optional()])
    api_key = fields.StringField('API Key')
