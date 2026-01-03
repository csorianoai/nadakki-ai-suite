"""Tests para adaptadores."""
import sys
import asyncio
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from adapters import (
    SocialNetworkRegistry, Platform, PostContent, PublishResult,
    MetaAdapter, TikTokAdapter, XAdapter
)


def run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def run_tests():
    print("\n" + "=" * 60)
    print(" NADAKKI ADAPTERS - TEST SUITE")
    print("=" * 60)
    
    passed, failed = 0, 0
    
    # Test 1
    try:
        assert SocialNetworkRegistry.count() >= 7
        print("  [OK] 7+ adapters registered")
        passed += 1
    except:
        print("  [FAIL] adapter count")
        failed += 1
    
    # Test 2
    try:
        adapter = SocialNetworkRegistry.get_adapter(Platform.FACEBOOK)
        assert isinstance(adapter, MetaAdapter)
        print("  [OK] MetaAdapter for Facebook")
        passed += 1
    except:
        print("  [FAIL] MetaAdapter")
        failed += 1
    
    # Test 3
    try:
        content = PostContent(text="Hello", hashtags=["test"])
        assert content.text == "Hello"
        print("  [OK] PostContent creation")
        passed += 1
    except:
        print("  [FAIL] PostContent")
        failed += 1
    
    # Test 4
    try:
        adapter = MetaAdapter()
        url = adapter.get_auth_url("tenant1", "http://callback.com")
        assert "facebook.com" in url
        print("  [OK] Auth URL generation")
        passed += 1
    except:
        print("  [FAIL] Auth URL")
        failed += 1
    
    # Test 5
    try:
        adapter = TikTokAdapter()
        content = PostContent(text="No video")
        result = run_async(adapter.publish_post(content))
        assert result.success == False
        print("  [OK] TikTok requires video")
        passed += 1
    except:
        print("  [FAIL] TikTok video check")
        failed += 1
    
    print(f"\n RESULTS: {passed} passed, {failed} failed")
    print("=" * 60 + "\n")
    return passed, failed


if __name__ == "__main__":
    run_tests()
