"""Creates a todo reminding you to read a random Wikipedia article.

Run as a one-off job; it posts to the backend's API and exits.
"""

import os
import sys

import httpx

TODO_BACKEND_URL = os.getenv("TODO_BACKEND_URL", "http://todo-backend-svc:2349")
MAX_TODO_LENGTH = int(os.getenv("MAX_TODO_LENGTH", 140))
RANDOM_ARTICLE_URL = "https://en.wikipedia.org/wiki/Special:Random"
TIMEOUT_SECONDS = 10
ATTEMPTS = 5
# Wikimedia rejects requests without a descriptive User-Agent.
USER_AGENT = "dwk-todo-app/1.0 (https://github.com/drellxor/KubernetesSolutions)"


def random_article_url() -> str:
    """Special:Random answers with a redirect, so read where it points."""
    response = httpx.get(
        RANDOM_ARTICLE_URL,
        headers={"User-Agent": USER_AGENT},
        timeout=TIMEOUT_SECONDS,
    )
    if not response.is_redirect:
        response.raise_for_status()
        raise httpx.HTTPError(f"expected a redirect, got {response.status_code}")

    # The Location header is protocol-relative, so let httpx resolve it.
    return str(response.next_request.url)


def pick_todo() -> str:
    """A todo the backend will accept.

    Percent-encoded article titles can be long enough to exceed the backend's
    limit, in which case another article is just as good a reminder.
    """
    for _ in range(ATTEMPTS):
        todo = f"Read {random_article_url()}"
        if len(todo) <= MAX_TODO_LENGTH:
            return todo
        print(
            f"Article URL too long ({len(todo)} characters), trying another",
            flush=True,
        )

    raise httpx.HTTPError(f"no article URL short enough after {ATTEMPTS} attempts")


def main() -> None:
    try:
        todo = pick_todo()
        response = httpx.post(
            f"{TODO_BACKEND_URL}/todos", json={"todo": todo}, timeout=TIMEOUT_SECONDS
        )
        response.raise_for_status()
    except httpx.HTTPError as error:
        # A non-zero exit lets Kubernetes count the job as failed and retry.
        print(f"Failed to create the todo: {error}", file=sys.stderr, flush=True)
        raise SystemExit(1) from error

    print(f"Created todo: {todo}", flush=True)


if __name__ == "__main__":
    main()
