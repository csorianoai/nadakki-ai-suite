"""
Nadakki AI Suite - Operational Wrapper
Decorator pattern: wraps an agent to optionally auto-publish results.
"""
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger("OperationalWrapper")


class OperationalWrapper:
    """Wraps a marketing agent to add auto-publish capability."""

    def __init__(self, agent, bridge=None):
        self.agent = agent
        self.bridge = bridge

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent, optionally publish via bridge."""
        # Run the underlying agent
        if hasattr(self.agent, "execute"):
            result = self.agent.execute(input_data)
        else:
            result = {"error": "Agent has no execute method"}

        # Handle async results
        if hasattr(result, "__await__"):
            result = await result

        published = False

        if input_data.get("auto_publish") and self.bridge:
            publish_content = self._extract_publishable(result, input_data)
            if publish_content:
                platform = input_data.get("platform", "meta")
                media_url = input_data.get("media_url")
                try:
                    pub_result = await self.bridge.publish(
                        platform=platform,
                        content=publish_content,
                        media_url=media_url,
                    )
                    result["publish_result"] = pub_result
                    published = pub_result.get("success", False) or pub_result.get(
                        "dry_run", False
                    )
                except Exception as e:
                    logger.error(f"Auto-publish failed: {e}")
                    result["publish_result"] = {"success": False, "error": str(e)}

        result["published"] = published
        return result

    @staticmethod
    def _extract_publishable(
        result: Dict[str, Any], input_data: Dict[str, Any]
    ) -> Optional[str]:
        """Extract publishable text from agent result."""
        for key in ("content", "text", "post", "message", "output", "generated_content"):
            if key in result and isinstance(result[key], str):
                return result[key]
        return input_data.get("content")
