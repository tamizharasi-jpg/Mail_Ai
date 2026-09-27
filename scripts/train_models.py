"""Train the same runtime baseline and print diagnostic metrics."""
from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).parents[1] / "backend"))
from ml_pipeline import MailMindPipeline  # noqa: E402


if __name__ == "__main__":
    bundle = MailMindPipeline().bundle
    output = Path(__file__).parents[1] / "models"
    output.mkdir(exist_ok=True)
    (output / "training_metrics.json").write_text(json.dumps(bundle.metrics, indent=2), encoding="utf-8")
    print(json.dumps(bundle.metrics, indent=2))