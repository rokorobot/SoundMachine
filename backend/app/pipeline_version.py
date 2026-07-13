"""Single source of truth for generation semantics (R23).

Bump this whenever an engine change alters output for identical input. The
golden-fixture test (T26) couples stored artifacts to this value so an
un-versioned engine change fails CI.
"""
PIPELINE_VERSION = "1.0.0-ws1"
