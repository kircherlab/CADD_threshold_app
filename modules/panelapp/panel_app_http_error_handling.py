import requests
import time
from requests.exceptions import RequestException


# Public constants for other modules to import without triggering network activity
headers = {"Accept": "application/json"}
URL = "https://panelapp.genomicsengland.co.uk/api/v1"


def get_with_retries(url, headers=None, max_retries=5, backoff_factor=1.0):
    """GET `url` with simple retry/backoff on 429 and transient errors.
    Returns a `requests.Response` or `None` if all retries fail.
    """
    attempt = 0
    while attempt < max_retries:
        try:
            resp = requests.get(url, headers=headers)
        except RequestException as e:
            wait = backoff_factor * (2**attempt)
            print(
                f"RequestException for {url}: {e}. Backing off {wait}s (attempt {attempt + 1}/{max_retries})"
            )
            time.sleep(wait)
            attempt += 1
            continue

        if resp.status_code == 200:
            return resp

        if resp.status_code == 429:
            # Honor Retry-After header when present, otherwise exponential backoff
            retry_after = resp.headers.get("Retry-After")
            if retry_after is not None:
                try:
                    wait = int(retry_after)
                except ValueError:
                    # could be a HTTP-date; fall back to exponential
                    wait = backoff_factor * (2**attempt)
            else:
                wait = backoff_factor * (2**attempt)

            print(
                f"Rate limited (429) for {url}. Waiting {wait}s (attempt {attempt + 1}/{max_retries})"
            )
            time.sleep(wait)
            attempt += 1
            continue

        # For other 5xx server errors, retry; for 4xx (other than 429) don't retry
        if 500 <= resp.status_code < 600:
            wait = backoff_factor * (2**attempt)
            print(
                f"Server error {resp.status_code} for {url}. Backing off {wait}s (attempt {attempt + 1}/{max_retries})"
            )
            time.sleep(wait)
            attempt += 1
            continue

        # Non-retryable status
        print(f"Request failed for {url}: {resp.status_code}")
        return resp

    print(f"Exceeded max retries for {url}")
    return None
