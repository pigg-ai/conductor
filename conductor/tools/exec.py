from typing import List, Tuple

from langroid.agent.tool_message import ToolMessage
import re
import importlib


class ExecTool(ToolMessage):
    request: str = "exec_tool"
    purpose: str = """
    Allowing agents to execute python code directly. 
    This is useful for calling subprocesses, running scripts, etc.
    """
    code: str

    @classmethod
    def examples(cls) -> List["ToolMessage" | Tuple[str, "ToolMessage"]]:
        return [
            (
                "I wanna look at current directory",
                cls(code="import os\nprint(os.listdir())"),
            ),
            (
                "I wanna ping google.com",
                cls(code="import subprocess\nsubprocess.run(['ping', 'google.com'])"),
            ),
        ]

    @classmethod
    def instructions(cls) -> str:
        return """
        Use this tool/function to run arbitrary python code directly.
        Rules: 
        1. BE EXTREMELY CAREFUL and DO NOT modify the system or any files outside of the working directory.
        2. DO not cause infite loops.
        3. EVERYTIME working with paths, use os.path.join() to prepend the working directory.
        """

    def handle(self) -> str:
        # Parse the imports using regex
        import_pattern = (
            r"^import\s+(\w+)(?:\s*,\s*\w+)*|^from\s+(\w+)(?:\.\w+)*\s+import"
        )
        imports = re.findall(import_pattern, self.code, re.MULTILINE)

        # Flatten and clean up the import list
        import_list = [imp for group in imports for imp in group if imp]

        # Validate the imports
        for module in import_list:
            try:
                importlib.import_module(module)
            except ImportError as e:
                return f"Error importing module '{module}': {str(e)}"

        # If all imports are valid, execute the code
        try:
            exec_globals = {}
            exec(self.code, exec_globals)

            # Capture print outputs
            output = exec_globals.get("__builtins__", {}).get("_print_output", "")
            return output if output else "Code executed successfully (no output)"
        except Exception as e:
            return f"Error executing code: {str(e)}"
