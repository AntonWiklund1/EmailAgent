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

async def main():
    """Test the EmailAgent with a sample input."""
    logger.info("Starting EmailAgent test...")

    with open("tmp/extracted_text.txt", "r") as f:
        extracted_text = f.read().strip()

    INPUT = f"""
    from: john@example.com
    subject: Monthly Invoice

    Here is the invoice for this month.

    Don't reply to this email.

    {extracted_text}"""

    NAME="Anton Wiklund"

    result = await invoke_email_agent(INPUT, NAME, datetime.datetime.now().strftime("%Y-%m-%d"), show_reasoning=True)

    if result is None:
        print("\n✅ Email processed successfully - no reply sent as requested.")
        return

    # Additional reasoning displays for successful responses
    print("\n🔍 COMPACT REASONING TRACE:")
    ReasoningDisplay.print_reasoning_trace(result)
    
    # Get structured summary for programmatic use
    reasoning_summary = ReasoningDisplay.get_reasoning_summary(result)
    print(f"\n📊 REASONING SUMMARY:")
    print(f"   • Tools Used: {len(reasoning_summary['tools_used'])}")
    print(f"   • Steps Taken: {len(reasoning_summary['reasoning_steps'])}")
    for tool in reasoning_summary['tools_used']:
        print(f"   • {tool['tool_name']}: {tool['reason']}")
    
    # Save detailed log for later analysis
    log_file = ReasoningDisplay.save_reasoning_log(result)
    
    # Original output logging
    logger.info("Final Result: %s", result.final_output)


if __name__ == "__main__":
   asyncio.run(main())