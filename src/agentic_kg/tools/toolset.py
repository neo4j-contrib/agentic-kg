from tkinter import Label
from typing import Callable, TypedDict, List

class ToolSet(TypedDict):
    """
    A set of tools intended to be used together.

    Attributes:
        name: The name of the tool set
        description: How the tools are used together
        tools: List of tools in the set
    """
    name: str
    description: str
    tools: List[Callable]

