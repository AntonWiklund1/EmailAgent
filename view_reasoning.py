"""
Simple utility to view reasoning logs
"""

import json
import sys
from datetime import datetime
from pathlib import Path


def view_reasoning_log(log_file: str):
    """View a reasoning log in a formatted way."""
    try:
        with open(log_file, 'r') as f:
            data = json.load(f)
        
        print(f"\n📋 REASONING LOG VIEWER")
        print(f"{'='*50}")
        print(f"📅 Timestamp: {data['timestamp']}")
        print(f"🤖 Agent: {data['agent_name']}")
        print(f"⚡ Model: {data['model']}")
        
        print(f"\n📥 INPUT:")
        print(f"   {data['input'][:200]}..." if len(data['input']) > 200 else f"   {data['input']}")
        
        summary = data.get('reasoning_summary', {})
        print(f"\n🔧 TOOLS USED ({len(summary.get('tools_used', []))}):")
        for tool in summary.get('tools_used', []):
            print(f"   • {tool['tool_name']}: {tool['reason']}")
        
        print(f"\n📤 FINAL OUTPUT:")
        print(f"   {data['final_output']}")
        
        print(f"\n{'='*50}")
        
    except Exception as e:
        print(f"❌ Error reading log file: {e}")


def list_reasoning_logs():
    """List all available reasoning logs."""
    logs = list(Path('.').glob('reasoning_log_*.json'))
    if not logs:
        print("No reasoning logs found in current directory.")
        return
    
    print(f"\n📚 AVAILABLE REASONING LOGS:")
    print(f"{'='*40}")
    
    for log in sorted(logs, reverse=True):  # Most recent first
        try:
            with open(log, 'r') as f:
                data = json.load(f)
            timestamp = data.get('timestamp', 'Unknown')
            agent_name = data.get('agent_name', 'Unknown')
            print(f"   📄 {log.name}")
            print(f"      └─ {timestamp} | {agent_name}")
        except:
            print(f"   📄 {log.name} (corrupted)")
    
    print(f"\n💡 Usage: python view_reasoning.py <filename>")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        list_reasoning_logs()
    else:
        view_reasoning_log(sys.argv[1])
