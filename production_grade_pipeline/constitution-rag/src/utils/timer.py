"""
Performance timing utilities.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Optional

from configs.logging import get_logger

logger = get_logger(__name__)


@dataclass
class TimingResult:
    """Result of a timing operation."""

    name: str
    elapsed_seconds: float
    start_time: float
    end_time: float

    @property
    def elapsed_ms(self) -> float:
        """Get elapsed time in milliseconds."""
        return self.elapsed_seconds * 1000

    def __str__(self) -> str:
        if self.elapsed_seconds < 1:
            return f"{self.name}: {self.elapsed_ms:.2f}ms"
        return f"{self.name}: {self.elapsed_seconds:.2f}s"


class Timer:
    """Context manager for timing code blocks."""

    def __init__(self, name: str = "Operation", log: bool = True):
        self.name = name
        self.log = log
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None

    def __enter__(self) -> Timer:
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        result = self.result

        if self.log:
            logger.info(str(result))

        return False

    @property
    def elapsed(self) -> float:
        """Get elapsed seconds."""
        if self.start_time is None:
            return 0.0

        end = self.end_time or time.time()
        return end - self.start_time

    @property
    def result(self) -> TimingResult:
        """Get the timing result."""
        return TimingResult(
            name=self.name,
            elapsed_seconds=self.elapsed,
            start_time=self.start_time or 0,
            end_time=self.end_time or time.time(),
        )


class PipelineTimer:
    """Track timing for multiple pipeline stages."""

    def __init__(self):
        self.stages: dict[str, list[float]] = {}
        self.current_stage: Optional[str] = None
        self.stage_start: Optional[float] = None

    def start(self, stage_name: str) -> None:
        """Start timing a stage."""
        if self.current_stage is not None:
            self.end()

        self.current_stage = stage_name
        self.stage_start = time.time()

    def end(self) -> float:
        """End timing the current stage."""
        if self.current_stage is None or self.stage_start is None:
            return 0.0

        elapsed = time.time() - self.stage_start

        if self.current_stage not in self.stages:
            self.stages[self.current_stage] = []

        self.stages[self.current_stage].append(elapsed)
        return elapsed

    def reset(self) -> None:
        """Reset all timings."""
        self.stages.clear()
        self.current_stage = None
        self.stage_start = None

    def get_total(self, stage_name: str) -> float:
        """Get total time for a stage."""
        if stage_name not in self.stages:
            return 0.0

        return sum(self.stages[stage_name])

    def get_average(self, stage_name: str) -> float:
        """Get average time for a stage."""
        if stage_name not in self.stages:
            return 0.0

        times = self.stages[stage_name]
        return sum(times) / len(times) if times else 0.0

    def get_count(self, stage_name: str) -> int:
        """Get number of times a stage ran."""
        return len(self.stages.get(stage_name, []))

    def summary(self) -> str:
        """Get a summary of all timings."""
        if not self.stages:
            return "No timing data"

        lines = ["=== Pipeline Timing Summary ==="]

        total_time = sum(
            sum(times) for times in self.stages.values()
        )
        lines.append(f"Total time: {total_time:.2f}s\n")

        for stage in sorted(self.stages.keys()):
            times = self.stages[stage]
            total = sum(times)
            avg = total / len(times)
            percentage = (total / total_time * 100) if total_time > 0 else 0

            lines.append(
                f"{stage:20s} | "
                f"Total: {total:7.2f}s | "
                f"Avg: {avg:6.2f}s | "
                f"Count: {len(times):3d} | "
                f"Pct: {percentage:5.1f}%"
            )

        return "\n".join(lines)

    def __str__(self) -> str:
        return self.summary()
