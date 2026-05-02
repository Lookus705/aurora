from __future__ import annotations

import argparse
from typing import Sequence

from .demo import SalonDemo, build_demo_state
from .storage import AppState


def build_cli_report(state: AppState, channel: str = "telegram") -> str:
    return SalonDemo(state).render_report(channel=channel)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="salon-mvp")
    subparsers = parser.add_subparsers(dest="command")

    report_parser = subparsers.add_parser("report", help="Muestra un reporte de demo")
    report_parser.add_argument("--channel", default="telegram", choices=["telegram", "whatsapp"])

    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.command in {None, "report"}:
        print(build_cli_report(build_demo_state(), channel=args.channel))
        return 0

    parser.print_help()
    return 1