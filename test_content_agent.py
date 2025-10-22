import asyncio
from datetime import datetime, timedelta
from agents.marketing.contentperformanceia import (
    ContentPerformanceIA, PerformanceAnalysisInput, ContentItem, ContentMetrics
)

async def test():
    agent = ContentPerformanceIA("tn_test_bank_001")
    
    now = datetime.now()
    
    content = [
        ContentItem(
            content_id="content_001",
            content_type="social_post",
            channel="instagram",
            publish_date=now - timedelta(days=2),
            title="Inversiones inteligentes",
            metrics=ContentMetrics(
                impressions=10000,
                reach=8000,
                engagement=400,
                clicks=120,
                shares=50,
                comments=30
            ),
            topic_tags=["finanzas", "inversiones"]
        ),
        ContentItem(
            content_id="content_002",
            content_type="blog_post",
            channel="blog",
            publish_date=now - timedelta(days=5),
            title="Guía de ahorro",
            metrics=ContentMetrics(
                impressions=5000,
                reach=3000,
                engagement=150,
                clicks=80,
                shares=20,
                comments=10
            ),
            topic_tags=["ahorro", "finanzas"]
        ),
        ContentItem(
            content_id="content_003",
            content_type="video",
            channel="youtube",
            publish_date=now - timedelta(days=1),
            title="Tutorial trading",
            metrics=ContentMetrics(
                impressions=15000,
                reach=12000,
                engagement=800,
                clicks=200,
                shares=100,
                comments=80,
                saves=50,
                watch_time_seconds=3600
            ),
            topic_tags=["trading", "inversiones"]
        ),
    ]
    
    inp = PerformanceAnalysisInput(
        tenant_id="tn_test_bank_001",
        content_items=content,
        analysis_period_days=7
    )
    
    result = await agent.execute(inp)
    print("✅ RESULTADO:", result.analysis_id)
    print("Contenidos analizados:", len(result.content_performances))
    
    if result.content_performances:
        print("\nTop performers:", result.top_performers[:3])
        print("\nTrending topics:")
        for trend in result.trending_topics[:3]:
            print(f"  {trend.topic}: {trend.frequency} posts, {trend.avg_engagement}% eng ({trend.trend_direction})")
        
        print("\nBenchmarks por canal:")
        for ch, eng in result.channel_benchmarks.items():
            print(f"  {ch}: {eng}%")
        
        print("\nPrimer análisis detallado:")
        p = result.content_performances[0]
        print(f"  Content: {p.content_id}")
        print(f"  Performance: {p.performance_level}")
        print(f"  Engagement: {p.engagement_rate}%")
        print(f"  Virality: {p.virality_score}/100")
    
    metrics = agent.get_metrics()
    print(f"\nMÉTRICAS: {metrics['ok']}/{metrics['total']}, Viral detected: {metrics.get('viral_detected', 0)}")
    print("\n✅ ContentPerformanceIA funciona")

asyncio.run(test())