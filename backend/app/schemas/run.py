from marshmallow import Schema, fields, validate


class RunSchema(Schema):
    id = fields.Str(dump_only=True)
    experiment_id = fields.Str(dump_only=True)
    name = fields.Str(dump_only=True)
    status = fields.Str(dump_only=True)
    hyperparameters = fields.Dict(dump_only=True)
    gpu_node_id = fields.Str(dump_only=True, allow_none=True)
    started_at = fields.DateTime(dump_only=True, allow_none=True)
    finished_at = fields.DateTime(dump_only=True, allow_none=True)
    created_at = fields.DateTime(dump_only=True)


class RunCreateSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    hyperparameters = fields.Dict(load_default=dict)


class RunStatusUpdateSchema(Schema):
    status = fields.Str(
        required=True,
        validate=validate.OneOf(["queued", "running", "completed", "failed"]),
    )
