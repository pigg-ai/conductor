import os
import typer


from typing import Optional, Union
from typing import TypedDict, Annotated
import asyncio

from semantic_kernel import Kernel
from semantic_kernel.functions import kernel_function
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel.connectors.ai.function_choice_behavior import (
    FunctionChoiceBehavior,
)
from semantic_kernel.connectors.ai.chat_completion_client_base import (
    ChatCompletionClientBase,
)
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.functions.kernel_arguments import KernelArguments

from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.azure_chat_prompt_execution_settings import (
    AzureChatPromptExecutionSettings,
)

from dotenv import load_dotenv

app = typer.Typer()


class LightModel(TypedDict):
    id: int
    name: str
    is_on: bool | None
    brightness: int | None
    hex: str | None


class LightsPlugin:
    lights: list[LightModel] = [
        {
            "id": 1,
            "name": "Table Lamp",
            "is_on": False,
            "brightness": 100,
            "hex": "FF0000",
        },
        {
            "id": 2,
            "name": "Porch light",
            "is_on": False,
            "brightness": 50,
            "hex": "00FF00",
        },
        {
            "id": 3,
            "name": "Chandelier",
            "is_on": True,
            "brightness": 75,
            "hex": "0000FF",
        },
    ]

    @kernel_function
    async def get_lights(self) -> Annotated[list[LightModel], "An array of lights"]:
        """Gets a list of lights and their current state."""
        return self.lights

    @kernel_function
    async def get_state(
        self, id: Annotated[int, "The ID of the light"]
    ) -> Annotated[LightModel | None, "The state of the light"]:
        """Gets the state of a particular light."""
        for light in self.lights:
            if light["id"] == id:
                return light
        return None

    @kernel_function
    async def change_state(
        self, id: Annotated[int, "The ID of the light"], new_state: LightModel
    ) -> Annotated[
        Optional[LightModel],
        "The updated state of the light; will return null if the light does not exist",
    ]:
        """Changes the state of the light."""
        for light in self.lights:
            if light["id"] == id:
                light["is_on"] = new_state.get("is_on", light["is_on"])
                light["brightness"] = new_state.get("brightness", light["brightness"])
                light["hex"] = new_state.get("hex", light["hex"])
                return light
        return None


async def main():
    load_dotenv()
    # Initialize the kernel
    kernel = Kernel()

    # Add Azure OpenAI chat completion
    chat_completion = OpenAIChatCompletion(ai_model_id="gpt-4o-mini")
    kernel.add_service(chat_completion)

    # Add a plugin (the LightsPlugin class is defined below)
    kernel.add_plugin(
        LightsPlugin(),
        plugin_name="Lights",
    )

    # Enable planning
    execution_settings = AzureChatPromptExecutionSettings(tool_choice="auto")
    execution_settings.function_choice_behavior = FunctionChoiceBehavior.Auto()
    # Create a history of the conversation
    history = ChatHistory()
    history.add_message(
        {
            "content": "Please turn on all the lights",
            "role": "user",
        }
    )

    # Get the response from the AI
    result = await chat_completion.get_chat_message_content(
        chat_history=history,
        settings=execution_settings,
        kernel=kernel,
    )

    # Print the results
    print("Assistant > " + str(result))

    # Add the message from the agent to the chat history
    history.add_message(result)


if __name__ == "__main__":
    asyncio.run(main())
