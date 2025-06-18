import datetime
from agents import Agent, Runner
import os
from dotenv import load_dotenv
from agent.context import UserInfo
from agent.prompt import SYSTEM_INSTRUCTION
from agent.tools import set_reminder_tool, send_urgent_message_tool, store_tool, dont_reply_tool
from agent.reasoning_display import ReasoningDisplay
from logger import setup_logger
import asyncio

load_dotenv()

logger = setup_logger()

MOCK_USERID = "mock_userid"

# class EmailOutput(BaseModel):
#     subject: str = Field(..., description="The subject of the email reply.")
#     body: str = Field(..., description="The body of the email reply.")


async def invoke_email_agent(input_text: str, user_name: str, current_date: str, show_reasoning: bool = False):
    """Invoke the EmailAgent with the provided input and user information."""
    INSTRUCTIONS = SYSTEM_INSTRUCTION.format(user_name=user_name, current_date=current_date)

    context = UserInfo(user_id=MOCK_USERID, user_email=os.getenv("EMAIL_USER"), original_input=input_text)

    email_agent = Agent(
        name="EmailAgent",
        instructions=INSTRUCTIONS,
        tools=[set_reminder_tool, send_urgent_message_tool, store_tool, dont_reply_tool],
        model="gpt-4.1-mini",
    )

    result =  await Runner.run(email_agent, input=input_text, context=context)

    if show_reasoning and result:
        print("\n" + "🎯 AGENT REASONING" + "\n")
        ReasoningDisplay.print_step_by_step_reasoning(result, show_details=True)
        print("\n" + "="*60)

    if context.abort_response:
        logger.info("Response aborted - no reply will be sent as requested.")
        if show_reasoning:
            print("\n🚫 FINAL DECISION: Response aborted - no reply will be sent.")
        return None

    logger.info("Agent execution completed successfully.")
    return result