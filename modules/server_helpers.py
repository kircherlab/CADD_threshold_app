"""Small server helper utilities used by `server_logic.py`.

Start with an `export_df_to_csv_string` helper to centralize CSV export logic
and keep the Shiny handler minimal and testable.
"""
from io import StringIO
import pandas as pd
import starlette.responses
from shiny import ui


def export_df_to_csv_string(df: pd.DataFrame, index: bool = False) -> str:
    """Return a CSV string for the provided DataFrame.

    Parameters
    - df: DataFrame to export
    - index: whether to include the index in the CSV (default False)

    Returns
    - CSV content as a str
    """
    buf = StringIO()
    df.to_csv(buf, index=index)
    buf.seek(0)
    return buf.getvalue()


def register_test_route(session):
    """Register a lightweight dynamic route that responds with 200 OK.

    Returns the URL string that the client can poll.
    """
    return session.dynamic_route(
        "test",
        lambda req: starlette.responses.PlainTextResponse(
            "OK", headers={"Cache-Control": "no-cache"}
        ),
    )


def make_connectivity_script(url: str):
    """Return a ui.tags.script element that polls the given URL.

    The script mirrors the original inline script used in `server_logic.out()`.
    """
    return ui.tags.script(
        f"""
            const url = "{url}";
            const count_el = document.getElementById("count");
            const status_el = document.getElementById("status");
            let count = 0;
            async function check_url() {{
                count_el.innerHTML = ++count;
                try {{
                    const resp = await fetch(url);
                    if (!resp.ok) {{
                        status_el.innerHTML = "Failure!";
                        return;
                    }} else {{
                        status_el.innerHTML = "In progress";
                    }}
                }} catch(e) {{
                    status_el.innerHTML = "Failure!";
                    return;
                }}

                if (count === 100) {{
                    status_el.innerHTML = "Test complete";
                    return;
                }}

                setTimeout(check_url, 10);
            }}
            check_url();
            """
    )
