import time

import requests
from requests.exceptions import RequestException

# Public constants for other modules to import without triggering network activity
headers = {"Accept": "application/json"}
URL = "https://panelapp.genomicsengland.co.uk/api/v1"


def _calculate_wait_time(retry_after, attempt, backoff_factor):
    """Calculate wait time based on Retry-After header or exponential backoff."""
    if retry_after is not None:
        try:
            return int(retry_after)
        except ValueError:
            # could be a HTTP-date; fall back to exponential
            return backoff_factor * (2**attempt)
    return backoff_factor * (2**attempt)


def _handle_request_exception(url, e, attempt, max_retries, backoff_factor):
    """Handle RequestException and perform backoff."""
    wait = backoff_factor * (2**attempt)
    print(
        f"RequestException for {url}: {e}. Backing off {wait}s (attempt {attempt + 1}/{max_retries})"
    )
    time.sleep(wait)


def _handle_rate_limit(url, resp, attempt, max_retries, backoff_factor, max_wait_cap):
    """Handle 429 rate limit response."""
    retry_after = resp.headers.get("Retry-After")
    wait = _calculate_wait_time(retry_after, attempt, backoff_factor)

    # Cap the wait to avoid very long pauses caused by large Retry-After values
    if isinstance(wait, (int, float)):
        wait = min(wait, max_wait_cap)

    print(
        f"Rate limited (429) for {url}. Waiting {wait}s (attempt {attempt + 1}/{max_retries})"
    )
    time.sleep(wait)


def _handle_server_error(url, resp, attempt, max_retries, backoff_factor):
    """Handle 5xx server errors."""
    wait = backoff_factor * (2**attempt)
    print(
        f"Server error {resp.status_code} for {url}. Backing off {wait}s (attempt {attempt + 1}/{max_retries})"
    )
    time.sleep(wait)


def get_with_retries(
    url, headers=None, max_retries=5, backoff_factor=1.0, timeout=10, max_wait_cap=60
):
    """GET `url` with simple retry/backoff on 429 and transient errors.
    Returns a `requests.Response` or `None` if all retries fail.
    """
    attempt = 0
    while attempt < max_retries:
        try:
            resp = requests.get(url, headers=headers, timeout=timeout)
        except RequestException as e:
            _handle_request_exception(url, e, attempt, max_retries, backoff_factor)
            attempt += 1
            continue

        if resp.status_code == 200:
            return resp

        if resp.status_code == 429:
            _handle_rate_limit(
                url, resp, attempt, max_retries, backoff_factor, max_wait_cap
            )
            attempt += 1
            continue

        # For other 5xx server errors, retry; for 4xx (other than 429) don't retry
        if 500 <= resp.status_code < 600:
            _handle_server_error(url, resp, attempt, max_retries, backoff_factor)
            attempt += 1
            continue

        # Non-retryable status
        print(f"Request failed for {url}: {resp.status_code}")
        return resp

    print(f"Exceeded max retries for {url}")
    return None
