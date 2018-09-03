from flask_restful import reqparse, inputs

story_list_query_parser = reqparse.RequestParser()
story_list_query_parser.add_argument("limit", type=int, default=500)
story_list_query_parser.add_argument("offset", type=int, default=0)
story_list_query_parser.add_argument(
    "order_by", default="id", choices=("id", "time", "score"))
story_list_query_parser.add_argument(
    "desc", type=inputs.boolean, default=False)


story_search_query_parser = story_list_query_parser.copy()
story_search_query_parser.add_argument("q", type=str, required=True)


url_stories_query_parser = reqparse.RequestParser()
url_stories_query_parser.add_argument("url", type=str, required=True)
