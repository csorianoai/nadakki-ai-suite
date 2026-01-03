# Nadakki Social Adapters v3.1

Enterprise social media integration.

## Platforms
- Facebook
- Instagram  
- TikTok
- X (Twitter)
- LinkedIn
- Pinterest
- YouTube

## Quick Start
```python
from adapters import SocialNetworkRegistry, Platform, PostContent

adapter = SocialNetworkRegistry.get_adapter(Platform.FACEBOOK)
content = PostContent(text="Hello!", hashtags=["ai"])
result = adapter.publish_post_sync(content)
```
