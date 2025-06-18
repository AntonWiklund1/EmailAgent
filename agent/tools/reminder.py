from agents import RunContextWrapper, function_tool
from pydantic import BaseModel, Field

from agent.context import UserInfo
from logger import setup_logger 

logger = setup_logger()


class ReminderRequest(BaseModel):
    reminder: str = Field(..., description="The reminder message to be set.")
    time: str = Field(..., description="The time when the reminder should trigger.")

@function_tool
def set_reminder_tool(wrapper: RunContextWrapper[UserInfo], reminder: ReminderRequest, reason: str) -> str:
    """
    Set a reminder for the user in their callender.
    """
    logger.info(f"Setting reminder tool called with reminder: {str(reminder)} for reason: {reason}")

    user_email = wrapper.context.user_email
    logger.info(f"Setting reminder for user {user_email}: {reminder.reminder} at {reminder.time}")

    return f"Reminder set for user {user_email}: '{reminder.reminder}' at {reminder.time}."