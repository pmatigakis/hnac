class HnacError(Exception):
    pass


class JobExecutionError(HnacError):
    pass


class ItemProcessingError(HnacError):
    pass
