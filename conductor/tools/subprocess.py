from typing import List, Tuple
import subprocess
import shlex

from langroid.agent.tool_message import ToolMessage


class SubprocessTool(ToolMessage):
    request: str = "subprocess_tool"
    purpose: str = """
    Allowing agents to manipulate subprocesses directly.
    """
    cmd: str
    max_timeout: int = 30  # Default timeout in seconds

    @classmethod
    def examples(cls) -> List["ToolMessage" | Tuple[str, "ToolMessage"]]:
        return [
            (
                "I wanna look at current directory",
                cls(cmd="ls -al"),
            ),
        ]

    @classmethod
    def instructions(cls) -> str:
        return """
        Use this tool/function to run arbitrary shell commands directly.
        """

    def handle(self) -> str:
        try:
            # Split the command string into a list of arguments
            cmd_args = shlex.split(self.cmd)

            # Run the command with a timeout
            result = subprocess.run(
                cmd_args,
                capture_output=True,
                text=True,
                timeout=self.max_timeout,
                check=True,
            )
            print(result.stdout)

            # Return the output of the command
            return result.stdout
        except subprocess.TimeoutExpired:
            return f"Command timed out after {self.max_timeout} seconds"
        except subprocess.CalledProcessError as e:
            return f"Command failed with exit code {e.returncode}. Error: {e.stderr}"
        except Exception as e:
            return f"An error occurred: {str(e)}"
