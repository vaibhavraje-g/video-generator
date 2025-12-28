"""Logging configuration to suppress internal library logs while keeping application logs"""

import logging
import sys
from typing import Optional


class ApplicationLogFilter(logging.Filter):
    """Filter to only allow logs from application modules"""

    def filter(self, record):
        # Allow logs from our application modules
        if record.name.startswith("app."):
            return True

        # Allow logs from the main script
        if record.name in ["__main__", "app.main", "app.scripts.js_interview_videos"]:
            return True

        # Suppress everything else (external libraries)
        return False


def setup_logging(level: int = logging.INFO, log_file: Optional[str] = None) -> None:
    """
    Setup logging configuration to suppress internal library logs

    Args:
        level: Logging level (default: INFO)
        log_file: Optional log file path
    """
    import warnings
    import os

    # 🧹 Suppress noisy warnings
    suppress_patterns = [
        ".*deprecated.*",
        ".*ALTS creds.*",
        ".*grpc.*",
        ".*absl::InitializeLog.*",
        ".*torch.backends.cuda.sdp_kernel.*",
        ".*Unexpected argument 'generation_config'.*",
        ".*LlamaModel is using LlamaSdpaAttention.*",
    ]
    for pattern in suppress_patterns:
        warnings.filterwarnings("ignore", message=pattern)
    warnings.filterwarnings("ignore", category=FutureWarning)
    warnings.filterwarnings("ignore", category=UserWarning)

    # 🧱 Suppress TensorFlow, gRPC, and other backend logs
    os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"  # TensorFlow C++ logs
    os.environ["GRPC_VERBOSITY"] = "ERROR"
    os.environ["GRPC_TRACE"] = ""
    os.environ["ABSL_LOG_SEVERITY_THRESHOLD"] = "fatal"
    os.environ["TOKENIZERS_PARALLELISM"] = "false"

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%H:%M:%S"
    )

    # Root logger setup
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Clear existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Console handler with filter
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(ApplicationLogFilter())
    root_logger.addHandler(console_handler)

    # Optional file handler
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        file_handler.addFilter(ApplicationLogFilter())
        root_logger.addHandler(file_handler)

    # 🔇 Suppress noisy third-party libraries
    noisy_libraries = [
        "torch",
        "transformers",
        "moviepy",
        "requests",
        "urllib3",
        "absl",
        "google",
        "grpc",
        "tensorflow",
        "numpy",
        "PIL",
        "imageio",
        "ffmpeg",
        "selenium",
        "ddgs",
        "pixabay",
        "duckduckgo",
        "matplotlib",
        "cv2",
    ]
    for lib in noisy_libraries:
        logging.getLogger(lib).setLevel(logging.WARNING)
        logging.getLogger(lib).propagate = False

    # Further suppress system warnings and external chatter
    logging.getLogger("py.warnings").setLevel(logging.ERROR)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("aiohttp").setLevel(logging.WARNING)

    # Ensure our app logger remains visible
    app_logger = logging.getLogger("app")
    app_logger.setLevel(logging.INFO)

    # Optional: intercept stderr junk (C++ loggers like absl, grpc)
    sys.stderr = open(os.devnull, "w")


def suppress_all_external_logs():
    """Aggressively suppress all external library logs"""
    for name in logging.Logger.manager.loggerDict:
        if not name.startswith("app"):
            logging.getLogger(name).setLevel(logging.WARNING)
            logging.getLogger(name).propagate = False
