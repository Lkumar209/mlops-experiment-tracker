from marshmallow import Schema, fields, validate


class ArtifactSchema(Schema):
    id = fields.Str(dump_only=True)
    run_id = fields.Str(dump_only=True)
    name = fields.Str(dump_only=True)
    artifact_type = fields.Str(dump_only=True)
    uri = fields.Str(dump_only=True)
    size_bytes = fields.Int(dump_only=True, allow_none=True)
    checksum = fields.Str(dump_only=True, allow_none=True)
    parent_artifact_id = fields.Str(dump_only=True, allow_none=True)
    created_at = fields.DateTime(dump_only=True)


class ArtifactCreateSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    artifact_type = fields.Str(required=True, validate=validate.OneOf(["model", "dataset", "checkpoint", "log"]))
    uri = fields.Str(required=True, validate=validate.Length(min=1, max=2048))
    size_bytes = fields.Int(load_default=None)
    checksum = fields.Str(load_default=None)
    parent_artifact_id = fields.Str(load_default=None)
