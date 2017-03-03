from marshmallow import Schema, fields


def is_story_item(item_data):
    if not isinstance(item_data, dict):
        return False

    required_fields = set(["id", "type", "by", "descendants",
                           "score", "time", "title", "url"])

    fields = set(item_data.keys())

    if not required_fields.issubset(fields):
        return False

    if item_data["type"] != "story":
        return False

    return True


class HackernewsStorySchema(Schema):
    id = fields.Int()
    type = fields.Str()
    title = fields.Str()
    url = fields.Url()
    by = fields.Str()
    descendants = fields.Int()
    score = fields.Int()
    time = fields.Int()
