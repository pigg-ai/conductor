import langroid as lr

from conductor.core.subprocess_manager import SubprocessManager


class GlobalState(lr.utils.globals.GlobalState):
    pm: SubprocessManager = SubprocessManager()

    class Config:
        arbitrary_types_allowed = True
