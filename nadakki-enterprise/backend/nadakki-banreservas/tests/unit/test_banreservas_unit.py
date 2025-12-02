import pytest

class TestBanreservas:
    def test_tenant_creation(self, sample_tenant):
        assert sample_tenant["id"] is not None
        assert sample_tenant["name"] == "banreservas"
        assert sample_tenant["country"] == "US"

    def test_user_creation(self, sample_user, sample_tenant):
        assert sample_user["id"] is not None
        assert sample_user["email"] == "test@example.com"
        assert sample_user["tenant_id"] == sample_tenant["id"]

    def test_authentication_headers(self, auth_headers, sample_user):
        assert "Authorization" in auth_headers
        assert "X-Tenant-ID" in auth_headers
        assert auth_headers["X-Tenant-ID"] == sample_user["tenant_id"]

    @pytest.mark.parametrize("plan,tier", [
        ("starter", "basic"),
        ("professional", "advanced"),
        ("enterprise", "premium")
    ])
    def test_subscription_plans(self, plan, tier):
        assert plan is not None
        assert tier is not None
