"""
Integration Test Script
Tests AI Router integration with OMEGA
"""

from ai_router_wrapper import get_ai_router
import os
import sys

def test_ai_router():
    """Test AI Router integration"""
    
    print("=" * 60)
    print("🧪 OMEGA + AI Router Integration Test")
    print("=" * 60)
    
    # Get router
    print("\n1️⃣ Initializing AI Router...")
    try:
        router = get_ai_router()
        print(f"   ✅ Router initialized: {router}")
    except Exception as e:
        print(f"   ❌ Failed to initialize: {e}")
        print("\n💡 Tip: Make sure you have:")
        print("   - config.py with GEMINI_API_KEY")
        print("   - ai/ folder in the same directory")
        return False
    
    # Test with sample file
    print("\n2️⃣ Testing file analysis...")
    
    # Find a test image
    test_paths = [
        "/mnt/user-data/uploads",
        ".",
        "../"
    ]
    
    test_file = None
    for path in test_paths:
        if os.path.exists(path):
            for root, dirs, files in os.walk(path):
                for file in files:
                    if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                        test_file = os.path.join(root, file)
                        break
                if test_file:
                    break
    
    if not test_file:
        print("   ⚠️  No test image found. Using dummy test...")
        print("   (This is OK - just means we can't test actual file analysis)")
        print("   ✅ AI Router initialized successfully though!")
    else:
        print(f"   📁 Test file: {test_file}")
        
        try:
            result, provider = router.analyze_file(test_file)
            
            print(f"\n   ✅ Analysis successful!")
            print(f"      Provider: {provider}")
            print(f"      Category: {result['category']}")
            print(f"      Price: ${result['price']}")
            print(f"      Tags: {result['tags'][:50]}...")
            
        except Exception as e:
            print(f"   ❌ Analysis failed: {e}")
            return False
    
    # Check stats
    print("\n3️⃣ Checking AI Router stats...")
    try:
        stats = router.get_stats()
        
        print(f"   ✅ Stats retrieved:")
        print(f"      Gemini calls: {stats['gemini_calls']}")
        print(f"      Gemini successes: {stats['gemini_successes']}")
        print(f"      Rate limits: {stats['gemini_rate_limits']}")
        print(f"      Fallbacks: {stats['total_fallbacks']}")
        print(f"      Web searches: {stats['web_searches']}")
        
    except Exception as e:
        print(f"   ❌ Stats failed: {e}")
        return False
    
    # Final verdict
    print("\n" + "=" * 60)
    print("🎉 Integration Test PASSED!")
    print("=" * 60)
    print("\n✅ AI Router is ready to use in OMEGA")
    print("✅ Next step: Run 'streamlit run app.py' and test Scanner")
    print()
    
    return True

if __name__ == "__main__":
    success = test_ai_router()
    sys.exit(0 if success else 1)
