from agents import RunContextWrapper, function_tool
from agent.context import UserInfo
from pydantic import BaseModel, Field
from logger import setup_logger

logger = setup_logger()

class ExtractedContent(BaseModel):
    due_date: str = Field(..., description="The due date extracted from the document.")
    amount: str = Field(..., description="The amount extracted from the document.")
    description: str = Field(..., description="A description of the document extracted.")
    category: str = Field(..., description="The category of the document extracted.")

@function_tool
def store_tool(wrapper: RunContextWrapper[UserInfo], extracted_content: ExtractedContent, reason: str) -> str:
    """Stores information in a database."""
    user_email = wrapper.context.user_email

    logger.info(f"Storing information for user {user_email} for reason: {reason}")
    logger.info(f"Storing information for user {user_email}: {str(extracted_content)}")


    return f"Information stored for user {user_email} for reason: '{reason}'."
