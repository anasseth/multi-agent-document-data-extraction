#!/usr/bin/env python3
"""
Test script to verify that all imports work correctly
"""

def test_imports():
    """Test all imports to ensure they work"""
    try:
        # Test config imports
        from .config.settings import create_client, create_model
        print("✓ Config imports successful")
        
        # Test models imports
        from .models.data_models import AnalysisContext, Classification, DocumentAnalysis
        print("✓ Models imports successful")
        
        # Test tools imports
        from .tools.function_tools import fetch_document, get_page_content
        print("✓ Tools imports successful")
        
        # Test prompts imports
        from .prompts.agent_prompts import (
            INVOICE_PAGE_EXTRACTOR_PROMPT,
            TRIAGE_AGENT_PROMPT
        )
        print("✓ Prompts imports successful")
        
        # Test agents imports
        from .agents.agent_definitions import create_agents
        print("✓ Agents imports successful")
        
        print("\n🎉 All imports successful! The modular structure is working correctly.")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    test_imports()
