from unittest import TestCase, main

from hnac.web.queries.parsers import parse_query_argument, parse_data_types


class ParseQueryArgumentTests(TestCase):
    def test_parse_query_argument(self):
        query_string = "gender=male+age__gte=18+age__lte=50"
        query = parse_query_argument(query_string)
        self.assertEqual(
            query,
            [
                ("gender", "eq", "male"),
                ("age", "gte", "18"),
                ("age", "lte", "50")
            ]
        )


class ParseDataTypesTests(TestCase):
    def test_parse_data_types(self):
        query_arguments = [
            ("var1", "eq", "10"),
            ("var2", "eq", "10.5"),
            ("var3", "eq", "true"),
            ("var4", "eq", "hello world")
        ]

        converted_query_argumera = parse_data_types(
            query_arguments=query_arguments,
            datatype_mapping={
                "var1": int,
                "var2": float,
                "var3": bool,
            }
        )

        self.assertEqual(
            converted_query_argumera,
            [
                ("var1", "eq", 10),
                ("var2", "eq", 10.5),
                ("var3", "eq", True),
                ("var4", "eq", "hello world")
            ]
        )


if __name__ == "__main__":
    main()
