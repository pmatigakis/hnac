from flask_restplus import reqparse

story_list_query_parser = reqparse.RequestParser()
story_list_query_parser.add_argument("limit", type=int, default=500)
story_list_query_parser.add_argument("offset", type=int, default=0)
