from typing import List, Tuple
import subprocess
import shlex

from langroid.agent.tool_message import ToolMessage

processes_state = {}


class SubprocessTool(ToolMessage):
    request: str = "subprocess_tool"
    purpose: str = """
    Allowing agents to manipulate subprocesses directly.
    """
    process_name: str
    cmd: str
    max_timeout: int = 10  # Default timeout in seconds

    @classmethod
    def examples(cls) -> List["ToolMessage" | Tuple[str, "ToolMessage"]]:
        return [
            (
                "I wanna look at current directory",
                cls(process_name="current_dir", cmd="ls -al"),
            ),
        ]

    @classmethod
    def instructions(cls) -> str:
        return """
        Use this tool/function to utilize process manager 
        """

    def handle(self) -> tuple[str, str]:
        try:
            global processes_state
            if self.process_name in processes_state:
                process = processes_state[self.process_name]
                stdout, stderr = process.communicate(timeout=self.max_timeout)
            else:
                args = shlex.split(self.cmd)
                print(args)
                process = subprocess.Popen(
                    args,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    shell=True,  # kinda bad
                )
                processes_state[self.process_name] = process

                stdout, stderr = process.communicate(timeout=self.max_timeout)
            print(stdout, stderr)
            return stdout, stderr
        except subprocess.TimeoutExpired:
            return f"Command timed out after {self.max_timeout} seconds"
        except subprocess.CalledProcessError as e:
            return f"Command failed with exit code {e.returncode}. Error: {e.stderr}"
        except Exception as e:
            return f"An error occurred: {str(e)}"
