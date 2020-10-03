from marshmallow import Schema, fields, post_load

from hnac.models import HackernewsStoryItem


def is_story_item(item_data):
    if not isinstance(item_data, dict):
        return False

    if "type" not in item_data or item_data["type"] != "story":
        return False

    return True


class HackernewsStorySchema(Schema):
    id = fields.Int(required=True)
    type = fields.Str(required=True)
    title = fields.Str(required=True)
    url = fields.Url(required=True)
    by = fields.Str(required=True)
    descendants = fields.Int(required=True)
    score = fields.Int(required=True)
    time = fields.Int(required=True)

    @post_load(pass_original=True)
    def make_hackernews_story_item(self, data, original_data, **kwargs):
        return HackernewsStoryItem(raw_data=original_data, **data)
