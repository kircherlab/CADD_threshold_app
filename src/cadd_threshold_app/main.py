import os
import subprocess
import sys
from pathlib import Path

import click


@click.command()
@click.option("--host", default="127.0.0.1", show_default=True, help="Host to bind")
@click.option("--port", default=8080, type=int, show_default=True, help="Port to bind")
@click.option(
    "--data",
    type=click.Path(file_okay=False, dir_okay=True, exists=True, path_type=str),
    default=None,
    help="Directory containing precomputed input CSV files. Data can be downloaded via https://zenodo.org/records/19204078",
)
def main(host: str, port: int, data: str | None) -> None:

    env = os.environ.copy()
    if data:
        env["CADD_THRESHOLD_DATA_PATH"] = data
    if "CADD_THRESHOLD_DATA_PATH" in env:
        path = Path(env["CADD_THRESHOLD_DATA_PATH"]).expanduser().resolve()
        if not path.exists():
            print(f"Error: Provided data path does not exist: {path}")
            sys.exit(1)
    else:
        print(
            "No data path provided! Please provide a valid data path using --data or set the CADD_THRESHOLD_DATA_PATH environment variable."
        )
        sys.exit(1)

    # Verify the data path exists
    data_path = Path(env["CADD_THRESHOLD_DATA_PATH"]).expanduser().resolve()
    if not data_path.exists():
        print(f"Error: Data path does not exist: {data_path}")
        sys.exit(1)

    subprocess.run(
        [
            sys.executable,
            "-m",
            "shiny",
            "run",
            "--host",
            host,
            "--port",
            str(port),
            "cadd_threshold_app.app:app",
        ],
        check=True,
        env=env,
    )


if __name__ == "__main__":
    main()
