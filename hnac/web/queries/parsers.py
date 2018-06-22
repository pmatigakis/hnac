from hnac.web.queries.operations import EQ, LT, LTE, GT, GTE
from hnac.exceptions import InvalidQueryParsingOperation


def parse_query_argument(query_string):
    query = []

    parts = query_string.split("+")
    for part in parts:
        operation_components = part.split("=")
        if len(operation_components) != 2:
            raise InvalidQueryParsingOperation(part)

        variable_parts = operation_components[0].split("__")
        if len(variable_parts) > 2:
            raise InvalidQueryParsingOperation(part)
        elif len(variable_parts) == 1:
            variable_parts.append(EQ)

        variable_parts[1] = variable_parts[1].lower()
        if variable_parts[1] not in [EQ, LTE, LT, GTE, GT]:
            raise InvalidQueryParsingOperation(part)

        query.append((*variable_parts, operation_components[1]))

    return query


def parse_data_types(query_arguments, datatype_mapping):
    query = []

    for index, query_argument in enumerate(query_arguments):
        variable, operation, value = query_argument
        if variable in datatype_mapping:
            query.append((variable, operation,
                          datatype_mapping[variable](value)))
        else:
            query.append(query_argument)

    return query
