from agents import RunContextWrapper, function_tool
from pydantic import BaseModel, Field

from agent.context import UserInfo
from logger import setup_logger 

logger = setup_logger()


class UrgentRequest(BaseModel):
    message: str = Field(..., description="The reminder message to be set.")

@function_tool
def send_urgent_message_tool(wrapper: RunContextWrapper[UserInfo], urgent_request: UrgentRequest, reason: str) -> str:
    """Sends a sms message as an urgent reminder to the user."""
    logger.info("Using send_urgent_message_tool to send an urgent message for the reason: " + reason)
    user_email = wrapper.context.user_email

    # Here you would implement the logic to set the reminder, e.g., save to a database or schedule a task.
    # For demonstration, we will just return a confirmation message.

    return f"Urgent sms sent for user {user_email}: '{urgent_request.message}'."