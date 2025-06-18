from agents import RunContextWrapper, function_tool
from agent.context import UserInfo
from logger import setup_logger

logger = setup_logger()

@function_tool
def dont_reply_tool(wrapper: RunContextWrapper[UserInfo], reason: str):
    """When this tool is invoked it will not send a reply to the user."""
    logger.info(f"Aborting response for user {wrapper.context.user_email}: {reason}")
    wrapper.context.abort_response = True
    return f"Response aborted due to: {reason}"
    
