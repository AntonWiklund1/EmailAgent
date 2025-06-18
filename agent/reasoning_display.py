"""
Enhanced reasoning display utilities for EmailAgent
"""

import json
from datetime import datetime
from typing import List, Dict, Any
from agents.result import RunResult
from agents.items import ToolCallItem, ToolCallOutputItem, MessageOutputItem


class ReasoningDisplay:
    """Utility class to display agent reasoning in a structured way."""
    
    @staticmethod
    def print_step_by_step_reasoning(result: RunResult, show_details: bool = True) -> None:
        """
        Print a detailed, step-by-step breakdown of the agent's reasoning process.
        
        Args:
            result: The RunResult from the agent execution
            show_details: Whether to show detailed information like tool arguments
        """
        print("\n" + "="*60)
        print("🧠 AGENT REASONING BREAKDOWN")
        print("="*60)
        
        print(f"📋 Agent: {result.last_agent.name}")
        print(f"⚡ Model: {result.last_agent.model}")
        print(f"🕐 Execution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Show input analysis
        print(f"\n📥 INPUT ANALYSIS:")
        print(f"   {result.input[:100]}..." if len(result.input) > 100 else f"   {result.input}")
        
        # Process the conversation flow
        print(f"\n🔄 REASONING FLOW:")
        
        step_number = 1
        tool_calls = []
        tool_outputs = []
        final_message = None
        
        # Organize items by type
        for item in result.new_items:
            if isinstance(item, ToolCallItem):
                tool_calls.append(item)
            elif isinstance(item, ToolCallOutputItem):
                tool_outputs.append(item)
            elif isinstance(item, MessageOutputItem):
                final_message = item
        
        # Show reasoning for each tool call
        for i, tool_call in enumerate(tool_calls):
            print(f"\n   Step {step_number}: 🔧 DECISION TO USE TOOL")
            print(f"   └─ Tool: {tool_call.raw_item.name}")
            
            if show_details:
                # Parse and display arguments in a readable way
                try:
                    args = json.loads(tool_call.raw_item.arguments)
                    print(f"   └─ Reasoning: {args.get('reason', 'No reason provided')}")
                    
                    # Show other arguments (excluding reason)
                    other_args = {k: v for k, v in args.items() if k != 'reason'}
                    if other_args:
                        print(f"   └─ Parameters:")
                        for key, value in other_args.items():
                            if isinstance(value, dict):
                                print(f"      • {key}:")
                                for sub_key, sub_value in value.items():
                                    print(f"        - {sub_key}: {sub_value}")
                            else:
                                print(f"      • {key}: {value}")
                except json.JSONDecodeError:
                    print(f"   └─ Arguments: {tool_call.raw_item.arguments}")
            
            step_number += 1
        
        # Show tool execution results
        for i, output in enumerate(tool_outputs):
            print(f"\n   Step {step_number}: ✅ TOOL EXECUTION RESULT")
            print(f"   └─ Output: {output.output}")
            step_number += 1
        
        # Show final reasoning and response
        if final_message:
            print(f"\n   Step {step_number}: 💭 FINAL RESPONSE GENERATION")
            content = final_message.raw_item.content[0].text if final_message.raw_item.content else "No content"
            print(f"   └─ Generated Response: {content[:150]}..." if len(content) > 150 else f"   └─ Generated Response: {content}")
        
        print(f"\n📤 FINAL OUTPUT:")
        print(f"{result.final_output}")
        
        print("\n" + "="*60)

    @staticmethod
    def get_reasoning_summary(result: RunResult) -> Dict[str, Any]:
        """
        Extract a structured summary of the agent's reasoning process.
        
        Returns:
            Dictionary containing reasoning summary
        """
        summary = {
            "agent_name": result.last_agent.name,
            "model": result.last_agent.model,
            "input_length": len(result.input),
            "tools_used": [],
            "reasoning_steps": [],
            "final_output_length": len(result.final_output)
        }
        
        for item in result.new_items:
            if isinstance(item, ToolCallItem):
                try:
                    args = json.loads(item.raw_item.arguments)
                    tool_info = {
                        "tool_name": item.raw_item.name,
                        "reason": args.get('reason', 'No reason provided'),
                        "arguments": {k: v for k, v in args.items() if k != 'reason'}
                    }
                    summary["tools_used"].append(tool_info)
                    summary["reasoning_steps"].append(f"Used {item.raw_item.name}: {args.get('reason', 'No reason')}")
                except json.JSONDecodeError:
                    summary["tools_used"].append({
                        "tool_name": item.raw_item.name,
                        "arguments": item.raw_item.arguments
                    })
            elif isinstance(item, ToolCallOutputItem):
                summary["reasoning_steps"].append(f"Tool result: {item.output[:50]}...")
        
        return summary

    @staticmethod
    def print_reasoning_trace(result: RunResult) -> None:
        """Print a compact trace of the reasoning process."""
        print("\n🔍 REASONING TRACE:")
        trace_items = result.to_input_list()
        
        for i, item in enumerate(trace_items):
            if item.get('role') == 'user':
                print(f"  {i+1}. 👤 User Input: {item['content'][:80]}...")
            elif item.get('type') == 'function_call':
                print(f"  {i+1}. 🔧 Tool Call: {item['name']}")
                try:
                    args = json.loads(item['arguments'])
                    print(f"     └─ Reason: {args.get('reason', 'N/A')}")
                except:
                    pass
            elif item.get('type') == 'function_call_output':
                print(f"  {i+1}. ✅ Tool Result: {item['output'][:50]}...")
            elif item.get('role') == 'assistant':
                content = item.get('content', [{}])
                if content and content[0].get('text'):
                    print(f"  {i+1}. 🤖 Assistant: {content[0]['text'][:50]}...")

    @staticmethod
    def save_reasoning_log(result: RunResult, filename: str = None) -> str:
        """Save detailed reasoning log to a file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reasoning_log_{timestamp}.json"
        
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "agent_name": result.last_agent.name,
            "model": result.last_agent.model,
            "input": result.input,
            "final_output": result.final_output,
            "reasoning_summary": ReasoningDisplay.get_reasoning_summary(result),
            "full_trace": result.to_input_list()
        }

        with open(f"logs/{filename}", 'w') as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Reasoning log saved to: {filename}")
        return filename
