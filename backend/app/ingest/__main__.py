import argparse
import logging
from pathlib import Path

from app.ingest.consumer import run_live, run_replay

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

parser = argparse.ArgumentParser(prog="ingest")
parser.add_argument("--replay-file", type=Path, help="JSONL of CertStream messages")
args = parser.parse_args()

run_replay(args.replay_file) if args.replay_file else run_live()