from fastapi import Query

MAX_LIMIT = 50
MAX_SKIP  = 10_000

def LimitParam(default:int=10):
    return Query(default=default, ge=1, le=MAX_LIMIT, description=f"Items per page (max {MAX_LIMIT})")

def SkipParam(default:int=0):
    return Query(default=0, ge=0, le=MAX_SKIP, description=f"Items to skip (max {MAX_SKIP})")

def clamp_limit_skip(limit:int|None, skip:int|None):
    # Backstop in case any route forgets Query validators
    L = 10 if limit is None else max(1, min(limit, MAX_LIMIT))
    S = 0  if skip  is None else max(0, min(skip,  MAX_SKIP))
    return L, S
