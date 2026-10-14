"""
Command-line interface for the Hybrid RAG system.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from configs.logging import get_logger
from configs.settings import settings
from src.rag.pipeline import HybridRAGPipeline
from src.utils.logger import QueryLogger
from src.utils.timer import PipelineTimer

logger = get_logger(__name__)


class CLIInterface:
    """Command-line interface for RAG queries."""

    def __init__(self):
        self.pipeline = HybridRAGPipeline()
        self.timer = PipelineTimer()

    def query(
        self,
        question: str,
        show_sources: bool = True,
        show_timings: bool = False,
    ) -> None:
        """Execute a query and display results."""
        query_logger = QueryLogger(question)
        query_logger.log_start()

        self.timer.start("total")
        self.timer.start("query_execution")

        try:
            result = self.pipeline.query(question)
            elapsed_ms = self.timer.end() * 1000
            query_logger.log_generation(elapsed_ms)

            # Display answer
            print("\n" + "=" * 70)
            print("ANSWER:")
            print("=" * 70)
            print(result.answer)

            # Display sources if requested
            if show_sources and result.documents:
                print("\n" + "=" * 70)
                print("SOURCES:")
                print("=" * 70)
                for i, doc in enumerate(result.documents, 1):
                    source_info = f"{doc.metadata.source}"
                    if doc.metadata.article:
                        source_info += f", Article {doc.metadata.article}"
                    if doc.metadata.page:
                        source_info += f", Page {doc.metadata.page}"
                    print(f"{i}. {source_info} (Score: {doc.score:.2f})")

            self.timer.end()  # End total timing

            if show_timings:
                print("\n" + "=" * 70)
                print(self.timer.summary())
                print("=" * 70)

            query_logger.log_complete(self.timer.elapsed * 1000)

        except Exception as e:
            query_logger.log_error("query_execution", e)
            print(f"Error: {e}", flush=True)
            raise

    def interactive(self) -> None:
        """Start interactive query mode."""
        print("\n" + "=" * 70)
        print("Hybrid RAG Interactive Mode")
        print("=" * 70)
        print("Enter 'quit' or 'exit' to exit")
        print("Enter 'help' for help")
        print("=" * 70 + "\n")

        while True:
            try:
                question = input("Your question: ").strip()

                if not question:
                    continue

                if question.lower() in ["quit", "exit"]:
                    print("Goodbye!")
                    break

                if question.lower() == "help":
                    print(
                        "Enter any question about the Indian Constitution. "
                        "Type 'quit' to exit."
                    )
                    continue

                self.query(question, show_sources=True)
                print()

            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
                continue


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Hybrid RAG CLI for Indian Constitution",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s query "What are fundamental rights?"
  %(prog)s interactive
  %(prog)s batch questions.txt
        """,
    )

    subparsers = parser.add_subparsers(
        dest="command",
        help="Commands",
    )

    # Query command
    query_parser = subparsers.add_parser(
        "query",
        help="Run a single query",
    )
    query_parser.add_argument(
        "question",
        type=str,
        help="Question to ask",
    )
    query_parser.add_argument(
        "--no-sources",
        action="store_true",
        help="Don't show sources",
    )
    query_parser.add_argument(
        "--timings",
        action="store_true",
        help="Show performance timings",
    )

    # Interactive command
    subparsers.add_parser(
        "interactive",
        help="Start interactive mode",
    )

    # Batch command
    batch_parser = subparsers.add_parser(
        "batch",
        help="Process batch of questions",
    )
    batch_parser.add_argument(
        "input_file",
        type=str,
        help="File with questions (one per line)",
    )
    batch_parser.add_argument(
        "--output",
        "-o",
        type=str,
        help="Output file for results",
    )

    args = parser.parse_args()

    try:
        cli = CLIInterface()

        if args.command == "query":
            cli.query(
                question=args.question,
                show_sources=not args.no_sources,
                show_timings=args.timings,
            )

        elif args.command == "interactive":
            cli.interactive()

        elif args.command == "batch":
            cli.process_batch(
                input_file=args.input_file,
                output_file=args.output,
            )

        else:
            parser.print_help()

    except Exception as e:
        logger.error(f"CLI error: {e}")
        raise


if __name__ == "__main__":
    main()
