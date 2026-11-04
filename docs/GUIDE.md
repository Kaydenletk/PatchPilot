# selfheal: roadmap, progress, notes

Self-healing code agent: **AST static analysis → Docker sandbox → LLM patch loop (max 3 retries)**.

## Architecture
```
buggy code → 1. Static analyzer (ast) → 2. Controller loop → 3. Docker sandbox
                                              ↑   fail: stderr + violations back to LLM (max 3)
                                              └── pass: verified patch + coach report
```

## Working method
| Claude | User |
|---|---|
| boilerplate, models, config, Dockerfile, **tests (start red)** | writes the core logic of each module |
| explains each red failure, gives hints, reviews | runs tests, pastes red/green output |

Loop: red test → read the message → fix → green. Stuck 10 min → ask for a hint → still stuck → Claude shows and explains.

## Roadmap and progress
- [x] **Stage 0**: setup: `uv sync`, Docker running, `sandbox-runner:latest` image built
- [x] Warm-ups: pytest basics (`learn/lesson1`), Docker CLI walls (Lesson 2), Docker SDK (`learn/lesson3`)
- [ ] **Stage 1: Sandbox runner**: `src/selfheal/sandbox/runner.py::run_in_sandbox`
  - Tests: `tests/test_sandbox.py` (7 tests, all red at start). Order: passing → failing → two files → timeout → OOM → network → no leftover containers → hardening
  - Trap: `read_only=True` blocks `put_archive` into `/workspace`; the user picks a fix and explains why
- [ ] **Stage 2: AST rules engine**: `analysis/rules.py`, `analysis/engine.py` (`ast.NodeVisitor`: eval/exec, `open()` without `with`, raw SQL, I/O without try). Needs `Violation` model
- [ ] **Stage 3: Controller loop**: `agent/controller.py`, `agent/feedback.py`. Built with a FAKE runner and FAKE LLM first (Protocols), no API key or Docker needed
- [ ] **Stage 4: OpenAI wiring**: `agent/llm.py` (structured output returns the full fixed file; the diff is computed locally with `difflib`), prompts
- [ ] **Stage 5: Interfaces**: `report.py`, Rich CLI `cli.py`, Streamlit `app.py`
- [ ] **Stage 6: Demo scenarios + README**: `scenarios/a_memory_leak`, `b_eval`, `c_infinite_loop` (each with `buggy.py` and `test_buggy.py`)

Dependencies: Stage 3 uses 1 and 2; Stages 4 and 5 plug into 3; Stage 6 is wiring.

## Corrections to the original blueprint
1. `containers.run(timeout=...)` does not exist: use `wait(timeout=)` then `kill()`.
2. `detach=False` loses the exit code and OOM flag: use `create/start/wait`, then `reload()` for `State.OOMKilled`.
3. `python -c code` breaks on big code: copy files in with `put_archive`, run `pytest`.
4. One CPU constant (`CPU_QUOTA = 1.0`).
5. The LLM returns the **full fixed file**; the diff is computed locally.
6. Extra hardening: `memswap_limit == mem_limit`, `pids_limit`, `cap_drop=["ALL"]`, `no-new-privileges`, `read_only` + tmpfs `/tmp`, `user=1000`.

## Exit codes cheat sheet
`0` ok · `1` Python crash / test failed · `125` Docker itself failed · `137` killed (out of memory)

## Common gotchas seen so far
- Image name typo (`lastest` vs `latest`): check `docker images`.
- Docker log driver is `local`: `containers.run()` returns `None`.
- `echo $?` reports only the *last* command; chain with `;`.
- An empty or unsaved file gives `ImportError: cannot import name`; save with Cmd+S.
- Strings in quotes are text: `print("StatusCode")` ≠ `print(result["StatusCode"])`.

## Handy commands
```
uv run pytest tests/test_sandbox.py -v          # stage 1 tests
uv run pytest tests/test_sandbox.py -k timeout  # one test
docker ps -a                                    # leftover containers? (old row 5a992d68612c is unrelated)
uv run ruff check .
```
