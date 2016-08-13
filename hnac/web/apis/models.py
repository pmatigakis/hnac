from flask_restful import fields

story = {
    "id": fields.Integer,
    "title": fields.String,
    "url": fields.String,
    "time": fields.Integer,
    "by": fields.String,
    "score": fields.Integer,
    "descendants": fields.Integer
}
