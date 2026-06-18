from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .app import generate
from .domain.models import GenerationRequest, ValidationError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pink-noise")
    subparsers = parser.add_subparsers(dest="command", required=True)
    generate_parser = subparsers.add_parser("generate", help="generate calibration pink-noise reference tracks")
    generate_parser.add_argument("--profile", required=True)
    generate_parser.add_argument("--layout", required=True)
    generate_parser.add_argument("--output", required=True)
    generate_parser.add_argument("--channels", default="")
    generate_parser.add_argument("--duration", type=float)
    generate_parser.add_argument("--noise-mode", choices=["random", "periodic"])
    generate_parser.add_argument("--seed")
    generate_parser.add_argument("--overwrite", action="store_true")
    generate_parser.add_argument("--summary-name", default="SUMMARY.md")
    generate_parser.add_argument("--validation-name", default="validation-data.json")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "generate":
            request = GenerationRequest(
                profile_id=args.profile,
                layout_id=args.layout,
                output_directory=Path(args.output),
                target_channels=tuple(filter(None, (part.strip().lower() for part in args.channels.split(",")))),
                duration_seconds=args.duration,
                overwrite=args.overwrite,
                seed=args.seed,
                noise_mode=args.noise_mode,
                summary_name=args.summary_name,
                validation_name=args.validation_name,
            )
            result = generate(request)
            print(f"Generated {len(result.track_paths)} reference tracks")
            print(f"Summary: {result.summary_path}")
            print(f"Validation: {result.validation_path}")
            print(f"Calibration guide: {result.guide_path}")
            print(f"Status: {result.validation_data['overall_status']}")
            return 0
    except (ValidationError, OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    return 2
