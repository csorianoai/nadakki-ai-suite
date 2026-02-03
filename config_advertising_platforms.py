"""
ADVERTISING PLATFORMS CONFIGURATION
Multi-tenant, multi-platform advertising management
"""

class AdvertisingPlatforms:
    GOOGLE_ADS = "google_ads"
    META_ADS = "meta_ads"
    LINKEDIN_ADS = "linkedin_ads"
    TIKTOK_ADS = "tiktok_ads"
    PINTEREST_ADS = "pinterest_ads"
    YOUTUBE_ADS = "youtube_ads"
    TWITTER_ADS = "twitter_ads"
    SNAPCHAT_ADS = "snapchat_ads"
    
    @staticmethod
    def get_all_platforms():
        return [
            AdvertisingPlatforms.GOOGLE_ADS,
            AdvertisingPlatforms.META_ADS,
            AdvertisingPlatforms.LINKEDIN_ADS,
            AdvertisingPlatforms.TIKTOK_ADS,
            AdvertisingPlatforms.PINTEREST_ADS,
            AdvertisingPlatforms.YOUTUBE_ADS,
            AdvertisingPlatforms.TWITTER_ADS,
            AdvertisingPlatforms.SNAPCHAT_ADS,
        ]

PLATFORM_CONFIGS = {
    "google_ads": {
        "name": "Google Ads",
        "icon": "🔍",
        "description": "Search, Display, Shopping, YouTube ads",
        "kpis": ["impressions", "clicks", "conversions", "cpc", "roas"],
        "supported_industries": ["financial_services", "retail", "ecommerce"],
    },
    "meta_ads": {
        "name": "Meta Ads (Facebook & Instagram)",
        "icon": "📱",
        "description": "Facebook, Instagram, Messenger, Audience Network",
        "kpis": ["impressions", "clicks", "reach", "ctr", "cpc", "roas"],
        "supported_industries": ["financial_services", "retail", "boat_rental"],
    },
    "linkedin_ads": {
        "name": "LinkedIn Ads",
        "icon": "💼",
        "description": "B2B targeting, sponsored content, InMail",
        "kpis": ["impressions", "clicks", "conversions", "cpc", "engagement"],
        "supported_industries": ["financial_services", "b2b"],
    },
    "tiktok_ads": {
        "name": "TikTok Ads",
        "icon": "🎵",
        "description": "Video ads, brand partnerships, creator collaborations",
        "kpis": ["views", "clicks", "conversions", "cpv", "engagement"],
        "supported_industries": ["retail", "entertainment", "fashion"],
    },
    "pinterest_ads": {
        "name": "Pinterest Ads",
        "icon": "📌",
        "description": "Promoted Pins, Idea Pins, Shopping Ads",
        "kpis": ["impressions", "clicks", "conversions", "cpc", "roas"],
        "supported_industries": ["retail", "fashion", "home_decor"],
    },
    "youtube_ads": {
        "name": "YouTube Ads",
        "icon": "▶️",
        "description": "In-stream, discovery, bumper ads",
        "kpis": ["views", "clicks", "watch_time", "cpv", "engagement"],
        "supported_industries": ["all"],
    },
    "twitter_ads": {
        "name": "Twitter/X Ads",
        "icon": "𝕏",
        "description": "Promoted tweets, trends, conversations",
        "kpis": ["impressions", "clicks", "engagement", "ctr"],
        "supported_industries": ["all"],
    },
    "snapchat_ads": {
        "name": "Snapchat Ads",
        "icon": "👻",
        "description": "Snap Ads, Story Ads, filters, lenses",
        "kpis": ["impressions", "clicks", "conversions", "engagement"],
        "supported_industries": ["retail", "entertainment", "fashion"],
    },
}

DOMINICAN_BANKS = [
    "banreservas", "banco_popular", "banco_bhd", "banco_santa_cruz", "scotiabank",
    "asociacion_popular", "asociacion_cibao", "banco_promerica", "banco_caribe",
    "asociacion_nacional", "banesco", "banco_agricola", "banco_bdi",
    "banco_lopez_haro", "citibank", "banco_vimenca", "banco_ademi", "bandex",
    "banco_lafise", "banfondesa", "motor_credito", "alaver", "banco_adopem",
]
