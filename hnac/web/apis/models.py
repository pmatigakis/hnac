from flask_restplus import Model, fields

brief_story = Model("BriefStory", {
    "id": fields.Integer(required=True),
    "title": fields.String(required=True),
    "url": fields.String(required=True)
})


story = Model("Story", {
    "id": fields.Integer(required=True),
    "title": fields.String(required=True),
    "url": fields.String(required=True),
    "created_at": fields.DateTime(required=True),
    "username": fields.String(required=True),
    "score": fields.Integer(required=True),
    "comment_count": fields.Integer(required=True),
})
