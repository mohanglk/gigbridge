"""Background tasks (notifications, media processing, embeddings).

Wire these to a Redis-backed worker (ARQ or Celery) in Phase 2.
Keeping slow work out of request handlers from day one.
"""


def send_notification(user_id: int, message: str) -> None:
    raise NotImplementedError
