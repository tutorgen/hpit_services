from wtforms import form, fields, validators

class PluginForm(form.Form):
    name = fields.StringField('Plugin Name', validators=[validators.input_required()])
    description = fields.StringField('Plugin Description', validators=[validators.optional()])

