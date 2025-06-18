#!/usr/bin/env python3
"""
Interactive reasoning debugger for EmailAgent
"""

import json
import sys
from pathlib import Path


class InteractiveReasoningDebugger:
    """Interactive tool to debug agent reasoning step by step."""
    
    def __init__(self, log_file: str):
        """Initialize with a reasoning log file."""
        with open(log_file, 'r') as f:
            self.data = json.load(f)
        
        self.current_step = 0
        self.trace = self.data.get('full_trace', [])
        
    def start_debugging(self):
        """Start the interactive debugging session."""
        print("🐛 INTERACTIVE REASONING DEBUGGER")
        print("=" * 50)
        print("Commands:")
        print("  n/next    - Next step")
        print("  p/prev    - Previous step")
        print("  j/jump N  - Jump to step N")
        print("  l/list    - List all steps")
        print("  s/summary - Show summary")
        print("  q/quit    - Quit")
        print("=" * 50)
        
        self.show_current_step()
        
        while True:
            try:
                cmd = input("\n🔍 Debug> ").strip().lower()
                
                if cmd in ['q', 'quit']:
                    print("👋 Goodbye!")
                    break
                elif cmd in ['n', 'next']:
                    self.next_step()
                elif cmd in ['p', 'prev']:
                    self.prev_step()
                elif cmd.startswith('j') or cmd.startswith('jump'):
                    parts = cmd.split()
                    if len(parts) > 1:
                        try:
                            step_num = int(parts[1])
                            self.jump_to_step(step_num)
                        except ValueError:
                            print("❌ Invalid step number")
                    else:
                        print("❌ Please specify step number: j 3")
                elif cmd in ['l', 'list']:
                    self.list_all_steps()
                elif cmd in ['s', 'summary']:
                    self.show_summary()
                else:
                    print("❌ Unknown command. Type 'q' to quit.")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except EOFError:
                print("\n👋 Goodbye!")
                break
    
    def show_current_step(self):
        """Show the current step in detail."""
        if not self.trace:
            print("❌ No trace data available")
            return
            
        if self.current_step >= len(self.trace):
            print("🏁 End of trace")
            return
            
        step = self.trace[self.current_step]
        
        print(f"\n📍 STEP {self.current_step + 1} of {len(self.trace)}")
        print("-" * 30)
        
        if step.get('role') == 'user':
            print("👤 USER INPUT:")
            content = step.get('content', '')
            if len(content) > 200:
                print(f"   {content[:200]}...")
                print(f"   [Content truncated - {len(content)} chars total]")
            else:
                print(f"   {content}")
                
        elif step.get('type') == 'function_call':
            print(f"🔧 TOOL CALL: {step.get('name', 'Unknown')}")
            try:
                args = json.loads(step.get('arguments', '{}'))
                print(f"   📝 Reason: {args.get('reason', 'No reason provided')}")
                
                other_args = {k: v for k, v in args.items() if k != 'reason'}
                if other_args:
                    print("   📋 Parameters:")
                    for key, value in other_args.items():
                        if isinstance(value, dict):
                            print(f"      • {key}:")
                            for sub_key, sub_value in value.items():
                                print(f"        - {sub_key}: {sub_value}")
                        else:
                            print(f"      • {key}: {value}")
            except json.JSONDecodeError:
                print(f"   📋 Raw arguments: {step.get('arguments', 'None')}")
                
        elif step.get('type') == 'function_call_output':
            print("✅ TOOL RESULT:")
            output = step.get('output', 'No output')
            if len(output) > 150:
                print(f"   {output[:150]}...")
            else:
                print(f"   {output}")
                
        elif step.get('role') == 'assistant':
            print("🤖 ASSISTANT RESPONSE:")
            content = step.get('content', [])
            if content and content[0].get('text'):
                text = content[0]['text']
                if len(text) > 200:
                    print(f"   {text[:200]}...")
                else:
                    print(f"   {text}")
            else:
                print("   No content")
    
    def next_step(self):
        """Move to next step."""
        if self.current_step < len(self.trace) - 1:
            self.current_step += 1
            self.show_current_step()
        else:
            print("🏁 Already at the last step")
    
    def prev_step(self):
        """Move to previous step."""
        if self.current_step > 0:
            self.current_step -= 1
            self.show_current_step()
        else:
            print("🚀 Already at the first step")
    
    def jump_to_step(self, step_num: int):
        """Jump to a specific step."""
        if 1 <= step_num <= len(self.trace):
            self.current_step = step_num - 1
            self.show_current_step()
        else:
            print(f"❌ Step {step_num} doesn't exist. Valid range: 1-{len(self.trace)}")
    
    def list_all_steps(self):
        """List all steps with brief descriptions."""
        print(f"\n📋 ALL STEPS ({len(self.trace)} total):")
        print("-" * 40)
        
        for i, step in enumerate(self.trace):
            marker = "👉" if i == self.current_step else "  "
            
            if step.get('role') == 'user':
                print(f"{marker} {i+1:2d}. 👤 User input")
            elif step.get('type') == 'function_call':
                print(f"{marker} {i+1:2d}. 🔧 Tool call: {step.get('name', 'Unknown')}")
            elif step.get('type') == 'function_call_output':
                print(f"{marker} {i+1:2d}. ✅ Tool result")
            elif step.get('role') == 'assistant':
                print(f"{marker} {i+1:2d}. 🤖 Assistant response")
            else:
                print(f"{marker} {i+1:2d}. ❓ Unknown step type")
    
    def show_summary(self):
        """Show a summary of the entire reasoning process."""
        summary = self.data.get('reasoning_summary', {})
        
        print(f"\n📊 REASONING SUMMARY:")
        print("-" * 30)
        print(f"🤖 Agent: {summary.get('agent_name', 'Unknown')}")
        print(f"⚡ Model: {summary.get('model', 'Unknown')}")
        print(f"📥 Input length: {summary.get('input_length', 0)} chars")
        print(f"📤 Output length: {summary.get('final_output_length', 0)} chars")
        print(f"🔧 Tools used: {len(summary.get('tools_used', []))}")
        print(f"📋 Total steps: {len(summary.get('reasoning_steps', []))}")
        
        tools_used = summary.get('tools_used', [])
        if tools_used:
            print(f"\n🛠️  TOOLS BREAKDOWN:")
            for tool in tools_used:
                print(f"   • {tool['tool_name']}: {tool['reason']}")


def main():
    """Main function to start the debugger."""
    if len(sys.argv) < 2:
        # Find the most recent log file
        logs = list(Path('.').glob('reasoning_log_*.json'))
        if not logs:
            print("❌ No reasoning log files found.")
            print("💡 Run your EmailAgent first to generate logs.")
            return
        
        latest_log = max(logs, key=lambda x: x.stat().st_mtime)
        print(f"🔍 Using latest log: {latest_log}")
        log_file = str(latest_log)
    else:
        log_file = sys.argv[1]
    
    try:
        debugger = InteractiveReasoningDebugger(log_file)
        debugger.start_debugging()
    except FileNotFoundError:
        print(f"❌ File not found: {log_file}")
    except json.JSONDecodeError:
        print(f"❌ Invalid JSON in file: {log_file}")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
