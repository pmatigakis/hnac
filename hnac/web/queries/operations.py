EQ = "eq"
LTE = "lte"
LT = "lt"
GTE = "gte"
GT = "gt"


OPERATIONS = {
    EQ: lambda x, y: x == y,
    LTE: lambda x, y: x <= y,
    LT: lambda x, y: x < y,
    GTE: lambda x, y: x >= y,
    GT: lambda x, y: x > y
}
