import argparse
import subprocess
import sys


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the CADD Threshold Shiny app")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind")
    args = parser.parse_args()

    subprocess.run(
        [
            sys.executable,
            "-m",
            "shiny",
            "run",
            "--host",
            args.host,
            "--port",
            str(args.port),
            "cadd_threshold_app.app:app",
        ],
        check=True,
    )


if __name__ == "__main__":
    main()
