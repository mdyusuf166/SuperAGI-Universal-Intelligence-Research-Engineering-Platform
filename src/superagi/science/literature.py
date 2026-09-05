"""Boundary for future literature adapters; this module performs no network retrieval."""
def unavailable(query): return {"status":"UNAVAILABLE","query":query,"reason":"No literature provider configured; no citations fabricated."}
