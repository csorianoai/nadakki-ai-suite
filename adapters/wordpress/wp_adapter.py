"""
Nadakki WordPress Integration Adapter
Complete WordPress compatibility layer
"""
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, Optional, List
import hashlib
import hmac
from datetime import datetime
import json

class WordPressAdapter:
    def __init__(self, app: FastAPI):
        self.app = app
        self.setup_cors()
        self.setup_wordpress_routes()
    
    def setup_cors(self):
        """Configure CORS for WordPress integration"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=[
                "https://nadakki.com",
                "https://www.nadakki.com", 
                "http://localhost",
                "http://localhost:3000",
                "http://localhost:8080"
            ],
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            allow_headers=[
                "Content-Type",
                "Authorization", 
                "X-WordPress-Site",
                "X-WordPress-User",
                "X-Tenant-ID",
                "X-WP-Nonce"
            ],
        )
    
    def format_wp_response(self, data: Any = None, success: bool = True, 
                          message: str = "", error_code: str = None) -> Dict:
        """Format response for WordPress compatibility"""
        response = {
            "success": success,
            "data": data,
            "message": message,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        if error_code:
            response["error_code"] = error_code
            
        return response
    
    def validate_wp_request(self, request: Request) -> Dict:
        """Validate WordPress request headers and extract context"""
        wp_site = request.headers.get('X-WordPress-Site')
        wp_user = request.headers.get('X-WordPress-User') 
        wp_nonce = request.headers.get('X-WP-Nonce')
        tenant_id = request.headers.get('X-Tenant-ID')
        
        if not wp_site:
            raise HTTPException(
                status_code=400,
                detail=self.format_wp_response(
                    success=False,
                    message="Missing WordPress site header",
                    error_code="WP_SITE_MISSING"
                )
            )
        
        return {
            "wp_site": wp_site,
            "wp_user": wp_user,
            "wp_nonce": wp_nonce, 
            "tenant_id": tenant_id or "default"
        }
    
    def setup_wordpress_routes(self):
        """Setup WordPress-specific API routes"""
        
        @self.app.post("/api/v1/wp/evaluate")
        async def wp_evaluate_credit(request: Request):
            """WordPress-compatible credit evaluation endpoint"""
            try:
                wp_context = self.validate_wp_request(request)
                body = await request.json()
                
                # Process credit evaluation (integrate with your existing logic)
                result = await self.process_credit_evaluation(body, wp_context)
                
                return JSONResponse(
                    content=self.format_wp_response(
                        data=result,
                        success=True,
                        message="Credit evaluation completed successfully"
                    )
                )
                
            except HTTPException as e:
                return JSONResponse(
                    status_code=e.status_code,
                    content=e.detail
                )
            except Exception as e:
                return JSONResponse(
                    status_code=500,
                    content=self.format_wp_response(
                        success=False,
                        message=f"Internal server error: {str(e)}",
                        error_code="INTERNAL_ERROR"
                    )
                )
        
        @self.app.get("/api/v1/wp/agents")
        async def wp_get_agents(request: Request):
            """WordPress-compatible agents list endpoint"""
            try:
                wp_context = self.validate_wp_request(request)
                agents = await self.get_available_agents(wp_context["tenant_id"])
                
                return JSONResponse(
                    content=self.format_wp_response(
                        data={"agents": agents},
                        success=True,
                        message=f"Retrieved {len(agents)} agents"
                    )
                )
                
            except Exception as e:
                return JSONResponse(
                    status_code=500,
                    content=self.format_wp_response(
                        success=False,
                        message=str(e),
                        error_code="AGENTS_FETCH_ERROR"
                    )
                )
        
        @self.app.post("/api/v1/wp/auth")
        async def wp_authenticate(request: Request):
            """WordPress-compatible authentication endpoint"""
            try:
                body = await request.json()
                wp_site = request.headers.get('X-WordPress-Site')
                
                # Authenticate against WordPress (implement your logic)
                auth_result = await self.authenticate_wp_user(body, wp_site)
                
                return JSONResponse(
                    content=self.format_wp_response(
                        data=auth_result,
                        success=True,
                        message="Authentication successful"
                    )
                )
                
            except Exception as e:
                return JSONResponse(
                    status_code=401,
                    content=self.format_wp_response(
                        success=False,
                        message="Authentication failed",
                        error_code="WP_AUTH_FAILED"
                    )
                )
    
    async def process_credit_evaluation(self, data: Dict, wp_context: Dict) -> Dict:
        """Process credit evaluation with WordPress context"""
        # Integrate with your existing credit evaluation logic
        # This is where you'd call your similarity engine
        
        return {
            "evaluation_id": f"eval_{datetime.utcnow().timestamp()}",
            "risk_level": "medium",  # Replace with actual calculation
            "score": 0.72,           # Replace with actual score
            "recommendations": [
                "Standard approval process recommended",
                "Request additional income verification"
            ],
            "tenant_id": wp_context["tenant_id"],
            "processed_at": datetime.utcnow().isoformat()
        }
    
    async def get_available_agents(self, tenant_id: str) -> List[Dict]:
        """Get available agents for tenant"""
        # Replace with actual agent discovery logic
        return [
            {"name": "SentinelBot", "status": "active", "category": "monitoring"},
            {"name": "DNAProfiler", "status": "active", "category": "analysis"},
            {"name": "RiskOracle", "status": "active", "category": "evaluation"}
        ]
    
    async def authenticate_wp_user(self, auth_data: Dict, wp_site: str) -> Dict:
        """Authenticate WordPress user"""
        # Implement your WordPress authentication logic
        return {
            "token": "wp_auth_token_placeholder",
            "user_id": auth_data.get("user_id"),
            "tenant_id": auth_data.get("tenant_id", "default"),
            "expires_in": 3600
        }

def create_wordpress_adapter(app: FastAPI) -> WordPressAdapter:
    """Factory function to create WordPress adapter"""
    return WordPressAdapter(app)
