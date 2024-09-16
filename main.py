import langroid as lr
import typer
from conductor.tools.io import IOTool
from conductor.tools.exec import ExecTool
from conductor.tools.subprocess import SubprocessTool
from conductor.tools.browser import BrowserTool


lr.utils.logging.setup_colored_logging()

all_tools = [IOTool, ExecTool, SubprocessTool, BrowserTool]


app = typer.Typer()


def chat(tools: bool = False) -> None:
    config = lr.ChatAgentConfig(
        llm=lr.language_models.OpenAIGPTConfig(
            chat_model=lr.language_models.OpenAIChatModel.GPT4o_MINI,
        ),
        use_tools=tools,
        use_functions_api=not tools,
        vecdb=None,
    )
    conductor_agent = lr.ChatAgent(config)
    for tool in all_tools:
        conductor_agent.enable_message(tool)
    root_task = lr.Task(
        conductor_agent,
        name="RootTask",
        system_message="""
        You're an excellent software engineer with great expertise in web fulls tack development. You'll be given high level requirement from the customer and code up the solution.
        
        You have a set of tools that extends your capabilities, such as run subprocess commands, interact with file system, browser access, etc.
        
        
        Your job is to understand the requirements, ask clarifying questions if needed, code up the apps, debug and iterate, and finally optionally deploy the app, all using tools.

        """,
        llm_delegate=True,
        single_round=False,
    )
    root_task.run(
        "use the subprocess tool to create a next js starter app called next-demo, defualt timeout 10s"
    )


@app.command()
def main(
    debug: bool = typer.Option(False, "--debug", "-d", help="debug mode"),
    no_stream: bool = typer.Option(False, "--nostream", "-ns", help="no streaming"),
    nocache: bool = typer.Option(False, "--nocache", "-nc", help="don't use cache"),
    tools: bool = typer.Option(
        False,
        "--tools",
        "-t",
        help="use langroid tools instead of OpenAI function-calling",
    ),
) -> None:
    lr.utils.configuration.set_global(
        lr.utils.configuration.Settings(
            debug=debug,
            cache=not nocache,
            stream=not no_stream,
        )
    )
    chat(tools)


if __name__ == "__main__":
    app()
