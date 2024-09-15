from contextlib import contextmanager
from .subprocess_manager import SubprocessManager


@contextmanager
def subprocessmanager_context():
    """
    PROBLEM: so this is the context manager for subprocesses, we'd love to make it available
    for LLM agents as tooling to intereact with shell, spawn multiple processe, just like
    full-stack devs, and build a feedback-loop between the agent and the process.

    HOWEVER, there's no easy way of integrating this with the tooling ecosystem of langroid, we can't instantiate Tools and pass in arbitrary contexts.
    """
    sm = SubprocessManager()
    try:
        yield sm
    finally:
        sm.cleanup()
