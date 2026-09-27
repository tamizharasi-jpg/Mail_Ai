"""Evaluation entry point; accepts the baseline's diagnostic metrics for reproducibility."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[1] / "backend"))
from ml_pipeline import MailMindPipeline  # noqa: E402


if __name__ == "__main__":
    print(MailMindPipeline().bundle.metrics)