import subprocess
import threading
import queue
from typing import Optional


class LongRunningSubprocess:
    def __init__(self, command: str):
        self.command = command
        self.process: Optional[subprocess.Popen] = None
        self.output_queue = queue.Queue()
        self.should_stop = threading.Event()

    def start(self):
        if self.process is not None:
            raise RuntimeError("Process is already running")

        self.process = subprocess.Popen(
            self.command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
        )

        def enqueue_output():
            for line in iter(self.process.stdout.readline, ""):
                self.output_queue.put(line)
                if self.should_stop.is_set():
                    break
            self.process.stdout.close()

        self.thread = threading.Thread(target=enqueue_output)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        if self.process is None:
            return
        self.should_stop.set()
        self.process.terminate()
        self.process.wait()
        self.thread.join()
        self.process = None

    def get_output(self, timeout: float = 0.1) -> str:
        output = []
        while True:
            try:
                line = self.output_queue.get(block=True, timeout=timeout)
                output.append(line)
            except queue.Empty:
                break
        return "".join(output)


class SubprocessManager:
    """Manageing subprocesses in singleton.
    class variables:
        self.subprocesses: dict[str, LongRunningSubprocess] - mapping from subprocess name to LongRunningSubprocess object
    methods:
        self.start_subprocess(name: str, command: str) -> str - starts a subprocess with given name and command
        self.stop_subprocess(name: str) -> str - stops a subprocess with given name
        self.get_subprocess_output(name: str) -> str - gets the output of a subprocess with given name

    """

    def __init__(self):
        self.subprocesses = {}

    def start_subprocess(self, name: str, command: str) -> str:
        if name in self.subprocesses:
            return f"Subprocess '{name}' is already running"

        subprocess = LongRunningSubprocess(command)
        subprocess.start()
        self.subprocesses[name] = subprocess
        return f"Started subprocess '{name}' with command: {command}"

    def stop_subprocess(self, name: str) -> str:
        if name not in self.subprocesses:
            return f"No subprocess named '{name}' is running"

        self.subprocesses[name].stop()
        del self.subprocesses[name]
        return f"Stopped subprocess '{name}'"

    def get_subprocess_output(self, name: str) -> str:
        if name not in self.subprocesses:
            return f"No subprocess named '{name}' is running"

        return self.subprocesses[name].get_output()

    def cleanup(self):
        for name in list(self.subprocesses.keys()):
            self.stop_subprocess(name)
