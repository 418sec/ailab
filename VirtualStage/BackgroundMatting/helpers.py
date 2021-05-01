"""
Helper functions to ease dev burden.
"""
import subprocess


def spawn(args, **kwargs):
    """
    Executes an OS command, waits for it to complete, returns exit code.
    """
    return subprocess.call(args, **kwargs)