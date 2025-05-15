from marshmallow import Schema, fields, validate

class TodoSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True, validate=validate.Length(max=120))
    completed = fields.Bool(missing=False)
