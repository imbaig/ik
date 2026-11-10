"""TEST TARGET ONLY: real services with deterministic models, never the default app."""

from ui_harness import service

from music_store.deployment import serve

serve(service_factory=service, smoke_test=True)
