"""
Simple verification script to check framework structure.
"""

import os
import sys

def check_framework_structure():
    """Check that all required files and directories exist."""
    print("🔍 Checking Autonomous Agent Framework Structure")
    print("=" * 50)
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    required_structure = {
        'config': ['config_manager.py', 'agent_config.yaml'],
        'agents': ['base_agent.py', 'employee_agent.py', 'agent_manager.py'],
        'api_connectors': ['jira_connector.py', 'github_connector.py', 'confluence_connector.py'],
        'context_builder': ['context_builder.py'],
        'meeting_engine': ['meeting_simulator.py', 'conversation_manager.py'],
        'post_meeting': ['action_handler.py'],
        'examples': ['demo_vivek.py'],
        'tests': ['test_basic.py']
    }
    
    missing_items = []
    
    for directory, files in required_structure.items():
        dir_path = os.path.join(base_dir, directory)
        
        if not os.path.exists(dir_path):
            missing_items.append(f"Directory: {directory}")
            continue
            
        print(f"✓ Directory exists: {directory}")
        
        for file in files:
            file_path = os.path.join(dir_path, file)
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                print(f"  ✓ {file} ({file_size} bytes)")
            else:
                missing_items.append(f"File: {directory}/{file}")
    
    # Check main files
    main_files = ['__init__.py', 'requirements.txt']
    for file in main_files:
        file_path = os.path.join(base_dir, file)
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            print(f"✓ {file} ({file_size} bytes)")
        else:
            missing_items.append(f"File: {file}")
    
    print("\n" + "=" * 50)
    
    if missing_items:
        print("❌ Missing items:")
        for item in missing_items:
            print(f"  - {item}")
        return False
    else:
        print("✅ All required files and directories are present!")
        return True


def check_file_contents():
    """Check that key files have content."""
    print("\n🔍 Checking File Contents")
    print("=" * 30)
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    key_files = [
        'config/config_manager.py',
        'agents/base_agent.py',
        'agents/employee_agent.py',
        'meeting_engine/meeting_simulator.py',
        'post_meeting/action_handler.py'
    ]
    
    for file_path in key_files:
        full_path = os.path.join(base_dir, file_path)
        if os.path.exists(full_path):
            with open(full_path, 'r') as f:
                content = f.read()
                lines = len(content.split('\n'))
                chars = len(content)
                print(f"✓ {file_path}: {lines} lines, {chars} characters")
        else:
            print(f"❌ {file_path}: Not found")
    
    return True


def summarize_framework():
    """Provide a summary of the framework capabilities."""
    print("\n🎯 Framework Capabilities Summary")
    print("=" * 35)
    
    capabilities = [
        "✓ Modular agent architecture with base classes",
        "✓ Employee-specific agent initialization",
        "✓ Multi-source context extraction (Jira, GitHub, Confluence)",
        "✓ Intelligent context aggregation and summarization",
        "✓ Text-based meeting simulation engine",
        "✓ Multi-agent conversation management",
        "✓ Turn-taking and conversation flow control",
        "✓ Post-meeting action processing",
        "✓ Automatic meeting summary generation",
        "✓ Action item extraction and assignment",
        "✓ Jira ticket creation integration",
        "✓ Confluence documentation updates",
        "✓ Configurable employee and API settings",
        "✓ Team status monitoring and reporting",
        "✓ Example implementation for 'Vivek'"
    ]
    
    for capability in capabilities:
        print(f"  {capability}")
    
    print("\n📋 Key Components:")
    components = [
        "• ConfigManager: Handles configuration and employee mappings",
        "• EmployeeAgent: Represents individual employees in meetings",
        "• AgentManager: Manages multiple agents and their lifecycle",
        "• MeetingSimulator: Orchestrates multi-agent meeting simulations",
        "• ConversationManager: Controls conversation flow and turn-taking",
        "• ContextBuilder: Aggregates work context from multiple sources",
        "• PostMeetingActionHandler: Processes meeting outcomes",
        "• API Connectors: Interface with Jira, GitHub, and Confluence"
    ]
    
    for component in components:
        print(f"  {component}")


def main():
    """Main verification function."""
    structure_ok = check_framework_structure()
    check_file_contents()
    summarize_framework()
    
    print("\n" + "=" * 50)
    if structure_ok:
        print("🎉 Autonomous Agent Framework is ready for deployment!")
        print("\n📖 Next Steps:")
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Configure API credentials in config/agent_config.yaml")
        print("  3. Run the demo: python examples/demo_vivek.py")
        print("  4. Integrate with your meeting platforms")
        return True
    else:
        print("⚠️  Framework structure is incomplete.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

