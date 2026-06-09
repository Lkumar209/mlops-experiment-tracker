from marshmallow import Schema, fields, validate


class MetricSchema(Schema):
    id = fields.Str(dump_only=True)
    run_id = fields.Str(dump_only=True)
    key = fields.Str(dump_only=True)
    value = fields.Float(dump_only=True)
    step = fields.Int(dump_only=True)
    epoch = fields.Int(dump_only=True, allow_none=True)
    logged_at = fields.DateTime(dump_only=True)


class MetricPointSchema(Schema):
    key = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    value = fields.Float(required=True)
    step = fields.Int(required=True)
    epoch = fields.Int(load_default=None)


class MetricBulkIngestSchema(Schema):
    metrics = fields.List(fields.Nested(MetricPointSchema), required=True, validate=validate.Length(max=1000))
