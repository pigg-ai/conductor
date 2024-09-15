"""
A tool to write arbitrary files to the FS.
"""

import os
from typing import List, Tuple

from langroid.agent.tool_message import ToolMessage

WORKING_DIR = "_working_dir"


class IOTool(ToolMessage):
    request: str = "io_tool"
    purpose: str = """
    Allowing agents to interact with file system, such as writing codes to files.
    """
    file_path: str
    buffer: str

    @classmethod
    def examples(cls) -> List["ToolMessage" | Tuple[str, "ToolMessage"]]:
        return [
            (
                "I want to write the following code to file",
                cls(file_path="path/to/file", buffer="content"),
            )
        ]

    @classmethod
    def instructions(cls) -> str:
        return """
        Use this tool/function to write to a file. File path will be prefixed with the agent's working directory. return True if successful.
        """

    def handle(self) -> bool:
        fpath = os.path.join(WORKING_DIR, self.file_path)
        os.makedirs(os.path.dirname(fpath), exist_ok=True)
        with open(fpath, "w") as f:
            f.write(self.buffer)
        return True

    pass
