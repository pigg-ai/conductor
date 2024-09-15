from typing import List, Tuple, Optional, Any
from playwright.async_api import async_playwright, Page, Browser
from langroid.agent.tool_message import ToolMessage
import asyncio
import traceback


class BrowserTool(ToolMessage):
    """Flexible tool for interacting with browsers using Playwright APIs.
    TODO:
    1. finetune a LLM with expertise with playwright API, and is powerful enough to directly
    codegen the python code for playwright.
    2. we need some kind of safe mode to ensure codegen is valid, i.e. imports, versions,.

    """

    request: str = "browser_tool"
    purpose: str = """
    Allowing agents to interact with a browser directly using Playwright APIs.
    """
    code: str  # Python code using Playwright APIs
    max_timeout: int = 30  # Default timeout in seconds

    # class Config:
    #     arbitrary_types_allowed = True

    @classmethod
    def examples(cls) -> List["ToolMessage" | Tuple[str, "ToolMessage"]]:
        return [
            (
                "Navigate to a website",
                cls(code="await page.goto('https://www.example.com')"),
            ),
            (
                "Click a button with text 'Submit'",
                cls(code="await page.click('text=Submit')"),
            ),
        ]

    @classmethod
    def instructions(cls) -> str:
        return """
        Use this tool to interact with browsers using Playwright APIs. 
        Provide Python code that uses Playwright's `page` object to perform actions.
        The code will be executed in an async context, so use `await` for asynchronous operations.
        The code is wrapped in an async function `_execute()`
        """

    async def handle(self) -> Any:
        browser: Optional[Browser] = None
        page: Optional[Page] = None
        if browser is None:
            p = await async_playwright().start()
            browser = await p.chromium.launch()

        if page is None:
            page = await browser.new_page()

        try:
            # Create a local namespace with the page object
            local_ns = {"page": page}

            # Wrap the code in an async function
            wrapped_code = f"async def _execute():\n{self.code}"

            # Execute the wrapped code
            exec(wrapped_code, globals(), local_ns)

            # Run the function and get the result
            result = await asyncio.wait_for(
                local_ns["_execute"](), timeout=self.max_timeout
            )
            return result
        except asyncio.TimeoutError:
            return f"Operation timed out after {self.max_timeout} seconds."
        except Exception as e:
            return f"An error occurred: {str(e)}\n{traceback.format_exc()}"
        finally:
            if page:
                await page.close()
            if browser:
                await browser.close()
