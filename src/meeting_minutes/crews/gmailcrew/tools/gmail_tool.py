from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class GmailToolInput(BaseModel):
    """Input schema for MyCustomTool."""

    body: str = Field(..., description="The body of the email to send.")


class GmailTool(BaseTool):
    name: str = "GmailTool"
    description: str = (
        "Clear description for what this tool is useful for, your agent will need this information to use it."
    )
    args_schema: Type[BaseModel] = GmailToolInput

    def _run(self, argument: str) -> str:
        # Implementation goes here
        return "this is an example of a tool output, ignore it and move along."
