"""
Simple test script to verify basic framework functionality.
"""

import sys
import os
import asyncio
import logging
from datetime import datetime

# Add the parent directory to the path to import the framework
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from config.config_manager import ConfigManager, EmployeeConfig
    from agents.base_agent import WorkItem, Priority, ContextSummary
    from context_builder.context_builder import ContextBuilder
except ImportError:
    # Fallback for direct execution
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from config.config_manager import ConfigManager, EmployeeConfig
    from agents.base_agent import WorkItem, Priority, ContextSummary
    from context_builder.context_builder import ContextBuilder


def test_imports():
    """Test that all modules can be imported successfully."""
    print("Testing imports...")
    
    try:
        from config.config_manager import ConfigManager, AgentConfig, EmployeeConfig
        print("✓ Core config imports successful")
        
        from agents.employee_agent import EmployeeAgent
        from agents.agent_manager import AgentManager
        from agents.base_agent import BaseAgent, AgentOrchestrator
        print("✓ Agent modules imported successfully")
        
        from meeting_engine.meeting_simulator import MeetingSimulator
        from meeting_engine.conversation_manager import ConversationManager
        print("✓ Meeting engine modules imported successfully")
        
        from post_meeting.action_handler import PostMeetingActionHandler
        print("✓ Post-meeting modules imported successfully")
        
        from api_connectors.jira_connector import JiraConnector
        from api_connectors.github_connector import GitHubConnector
        from api_connectors.confluence_connector import ConfluenceConnector
        print("✓ API connector modules imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False


def test_data_models():
    """Test that data models work correctly."""
    print("\\nTesting data models...")
    
    try:
        # Test WorkItem creation
        work_item = WorkItem(
            id="TEST-123",
            title="Test work item",
            description="This is a test work item",
            status="In Progress",
            priority=Priority.HIGH,
            assignee="test_user",
            created_date="2024-01-01T10:00:00",
            updated_date="2024-01-02T10:00:00",
            source="test",
            labels=["test", "example"]
        )
        print("✓ WorkItem model works correctly")
        
        # Test EmployeeConfig creation
        employee_config = EmployeeConfig(
            name="Test User",
            employee_id="test_user",
            email="test@example.com",
            projects=["TEST-PROJECT"],
            teams=["test-team"],
            role="Test Engineer"
        )
        print("✓ EmployeeConfig model works correctly")
        
        return True
        
    except Exception as e:
        print(f"✗ Data model test failed: {e}")
        return False


def test_configuration():
    """Test configuration management."""
    print("\\nTesting configuration...")
    
    try:
        config_manager = ConfigManager()
        
        # Test sample config creation
        sample_config_path = "/tmp/test_agent_config.yaml"
        config_manager.create_sample_config(sample_config_path)
        print("✓ Sample configuration created successfully")
        
        # Test config loading
        if os.path.exists(sample_config_path):
            test_config_manager = ConfigManager(sample_config_path)
            config = test_config_manager.load_config()
            print("✓ Configuration loaded successfully")
            print(f"  - Found {len(config.employees)} employees")
            print(f"  - LLM model: {config.llm_model}")
            
            # Clean up
            os.remove(sample_config_path)
        
        return True
        
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False


async def test_context_builder():
    """Test context builder with mock data."""
    print("\\nTesting context builder...")
    
    try:
        # Create a simple context builder without real connectors
        context_builder = ContextBuilder()
        
        # Test with empty connectors (should handle gracefully)
        context = await context_builder.build_context("test_user", days_back=7)
        
        print("✓ Context builder handles empty connectors gracefully")
        print(f"  - Generated context for: {context.employee_id}")
        print(f"  - Active tasks: {len(context.active_tasks)}")
        print(f"  - Current focus: {context.current_focus}")
        
        return True
        
    except Exception as e:
        print(f"✗ Context builder test failed: {e}")
        return False


def main():
    """Run all basic tests."""
    print("🧪 Running Basic Framework Tests")
    print("=" * 40)
    
    # Configure logging
    logging.basicConfig(level=logging.WARNING)  # Reduce noise during testing
    
    tests = [
        ("Import Tests", test_imports),
        ("Data Model Tests", test_data_models),
        ("Configuration Tests", test_configuration),
        ("Context Builder Tests", lambda: asyncio.run(test_context_builder()))
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\\n--- {test_name} ---")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
    
    print("\\n" + "=" * 40)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All basic tests passed! Framework is ready for use.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

