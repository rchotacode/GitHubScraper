class RateLimitException(Exception):
    def __init__(self, message="Rate limit exceeded. Please try again later."):
        super().__init__(message)