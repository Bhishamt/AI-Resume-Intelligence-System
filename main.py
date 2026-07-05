import sys
import subprocess
import argparse
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def run_app(host: str, port: int):
    """Runs the Streamlit application."""
    logger.info(f"Launching Streamlit UI on {host}:{port}...")
    try:
        cmd = [
            "streamlit", "run", "ui/streamlit_app.py",
            "--server.address", host,
            "--server.port", str(port)
        ]
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        logger.info("Stopping application.")
    except Exception as e:
        logger.error(f"Error starting Streamlit: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Resume Intelligence System")
    parser.add_argument("--host", type=str, default="localhost", help="Host address to bind to")
    parser.add_argument("--port", type=int, default=8501, help="Port to bind to")
    args = parser.parse_args()
    
    run_app(args.host, args.port)
