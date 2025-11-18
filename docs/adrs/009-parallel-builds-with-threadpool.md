# ADR-009: Parallel Builds with ThreadPoolExecutor

**Status:** Accepted

**Date:** 2025-11-18

## Context

Full build matrix (2 languages × 2 flavors × 11 formats = 44 combinations) takes time if run sequentially. Conversions are I/O-bound (calling external tools), making them good candidates for parallelization.

Options:
- **Sequential**: Simple but slow
- **Multiprocessing**: Full CPU parallelism but high overhead
- **Threading**: Lighter weight, good for I/O-bound tasks
- **Async/await**: Complex for subprocess calls

## Decision

Use **ThreadPoolExecutor** from Python's `concurrent.futures` with:
- Default 4 workers (configurable in `build.yaml`)
- Thread pool for I/O-bound external tool calls
- Simple futures-based result collection
- Error collection (continue on failure)

## Consequences

**Positive:**
- **Speed**: 4x faster builds (4 workers)
- **Simple**: ThreadPoolExecutor is straightforward
- **Configurable**: Users can adjust worker count
- **Resource efficient**: Threads lighter than processes
- **Good for I/O**: External tool calls release GIL

**Negative:**
- **Not fully parallel**: GIL limits CPU parallelism
- **Complexity**: Concurrent errors harder to debug
- **Resource contention**: Too many workers can overwhelm system

**Mitigation:**
- Reasonable default (4 workers)
- Documented max_workers configuration
- Error handling collects all failures before reporting
- Subprocess calls release GIL (I/O-bound workload)
