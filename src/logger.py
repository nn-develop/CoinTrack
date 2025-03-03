import logging
import os


def setup_logging() -> None:
    """
    Configures the logging system to log to both a file in the 'data/logs' directory
    and the console.

    The logs are stored in the 'data/cointrack.log' file, and logs are also
    shown in the console.
    """
    # Ensure that the 'data/logs' directory exists
    log_dir: str = os.path.join(os.getcwd(), "data")
    os.makedirs(log_dir, exist_ok=True)  # Create the directory if it doesn't exist

    log_file: str = os.path.join(log_dir, "cointrack.log")

    # Set up logging configuration
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file),  # Log to the file
            logging.StreamHandler(),  # Log to the console
        ],
    )


# A reference to the root logger
logger: logging.Logger = logging.getLogger(__name__)
