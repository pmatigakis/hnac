class HnacError(Exception):
    pass


class JobExecutionError(HnacError):
    pass


class ItemProcessingError(HnacError):
    pass


class ModelSearchError(HnacError):
    pass


class UnsupportedSearchOperation(ModelSearchError):
    def __init__(self, variable=None, operation=None):
        super(UnsupportedSearchOperation, self).__init__(
            "unsupported search operation {} for "
            "variable {}".format(operation, variable)
        )

        self.operation = operation
        self.variable = variable


class QueryParsingError(HnacError):
    pass


class InvalidQueryParsingOperation(QueryParsingError):
    def __init__(self, operation=None):
        super(InvalidQueryParsingOperation, self).__init__(
            "invalid query operation {}".format(operation))

        self.operation = operation
