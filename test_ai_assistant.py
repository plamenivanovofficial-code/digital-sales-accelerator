"""
Test AI Assistant functionality
"""
import sys
import os

# Test imports
print("Testing imports...")
try:
    import config
    print("✓ config imported")
except Exception as e:
    print(f"✗ config import failed: {e}")
    sys.exit(1)

try:
    import ai_engine
    print("✓ ai_engine imported")
except Exception as e:
    print(f"✗ ai_engine import failed: {e}")
    sys.exit(1)

try:
    import ui_components
    print("✓ ui_components imported")
except Exception as e:
    print(f"✗ ui_components import failed: {e}")
    sys.exit(1)

# Test API key
print("\nChecking API key...")
if config.GEMINI_API_KEY:
    print(f"✓ API key found (length: {len(config.GEMINI_API_KEY)})")
else:
    print("✗ WARNING: No GEMINI_API_KEY found in config!")
    print("  Set it in .env file: GEMINI_API_KEY=your_key_here")

# Test AI function exists
print("\nChecking AI functions...")
if hasattr(ai_engine, 'ai_business_consultant'):
    print("✓ ai_business_consultant function exists")
else:
    print("✗ ai_business_consultant function NOT FOUND")

# Test UI function
if hasattr(ui_components, 'render_chat_message'):
    print("✓ render_chat_message function exists")
else:
    print("✗ render_chat_message function NOT FOUND")

# Test AI model availability
print("\nChecking AI models...")
try:
    models = ai_engine.list_available_models()
    if models:
        print(f"✓ Found {len(models)} available models:")
        for m in sorted(models):
            print(f"  - {m}")
    else:
        print("⚠ No models found (API key may be invalid)")
except Exception as e:
    print(f"✗ Error listing models: {e}")

# Test AI call (if API key exists)
if config.GEMINI_API_KEY:
    print("\nTesting AI call...")
    try:
        test_context = {
            "inventory_value": 1000,
            "ready_to_list": 5,
            "approved_assets_count": 10
        }
        
        response = ai_engine.ai_business_consultant(
            "Hello, can you help me?", 
            context=test_context
        )
        
        if isinstance(response, dict) and 'response' in response:
            print("✓ AI call successful!")
            print(f"  Response preview: {response['response'][:100]}...")
            if response.get('suggested_tasks'):
                print(f"  Suggested tasks: {len(response['suggested_tasks'])}")
        else:
            print(f"✗ Unexpected response format: {type(response)}")
    except Exception as e:
        print(f"✗ AI call failed: {e}")
else:
    print("\nSkipping AI call test (no API key)")

print("\n" + "="*60)
print("AI ASSISTANT DIAGNOSTIC COMPLETE")
print("="*60)
