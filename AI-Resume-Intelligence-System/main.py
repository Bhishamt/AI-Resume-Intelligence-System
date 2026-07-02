import sys
import subprocess

def run_app():
    """Runs the Streamlit application."""
    print("Launching Streamlit UI...")
    try:
        subprocess.run(["streamlit", "run", "ui/streamlit_app.py"], check=True)
    except KeyboardInterrupt:
        print("\nStopping application.")
    except Exception as e:
        print(f"Error starting Streamlit: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_app()
