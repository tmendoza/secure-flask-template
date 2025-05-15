from marshmallow import Schema, fields, validate

class TodoSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True, validate=validate.Length(max=120))
    # Marshmallow 4+: use load_default instead of missing
    completed = fields.Bool(load_default=False)
