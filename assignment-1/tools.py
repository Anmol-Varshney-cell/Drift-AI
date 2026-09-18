"""
Custom Research Tools for Assignment 1: Tool-Using Research Agent.
Provides at least 3 distinct tools with realistic domain data and controllable failure modes.
"""

import json
from typing import Dict, Any, Optional

# Global flag to control failure injection for grading verification
SIMULATE_TOOL_FAILURE = False

def set_simulate_tool_failure(value: bool):
    global SIMULATE_TOOL_FAILURE
    SIMULATE_TOOL_FAILURE = value

def architecture_docs_search(query: str) -> str:
    """
    Search engineering knowledge base for caching strategies, architecture patterns,
    invalidation mechanics, and handling personalized dynamic data.
    """
    query_lower = query.lower()
    
    if "redis" in query_lower or "cache-aside" in query_lower:
        return json.dumps({
            "topic": "Redis Cache-Aside Pattern",
            "read_heavy_performance": "Sub-millisecond read latency (0.5ms - 1.5ms) over internal VPC.",
            "dynamic_data_support": "Excellent for user-specific data via partitioned keys (e.g., user:session:{id}).",
            "invalidation_strategy": "Direct write-through or cache eviction on mutation. Near instantaneous cache invalidation.",
            "operational_overhead": "Requires cluster management, high availability sentinel/cluster mode, memory sizing for 10k req/sec."
        }, indent=2)
        
    elif "cloudflare" in query_lower or "cdn" in query_lower or "edge" in query_lower:
        return json.dumps({
            "topic": "Cloudflare CDN / Edge Caching",
            "read_heavy_performance": "Global edge delivery (10ms - 30ms latency to end user vs 80ms+ roundtrip to origin).",
            "dynamic_data_support": "Traditionally difficult for user-specific data without edge compute (Workers/KV) or Cache-Control: private.",
            "invalidation_strategy": "Purge by tag/URL takes 150ms-500ms; stale-while-revalidate recommended.",
            "best_use_case": "Static assets, semi-static API responses, public catalog/pricing data. For user data, requires Edge Workers with JWT parsing."
        }, indent=2)
        
    elif "hybrid" in query_lower or "combine" in query_lower or "recommendation" in query_lower:
        return json.dumps({
            "topic": "Two-Tier Hybrid Caching Architecture",
            "pattern": "L1 CDN Edge (public/shared data with short TTL + stale-while-revalidate) + L2 Redis Cluster (user-specific sessions & hot records).",
            "throughput_capability": "Easily absorbs 10k-50k req/sec while offloading 85%+ requests before hitting origin databases.",
            "tradeoffs": "Increased architectural complexity and two invalidation surfaces to maintain."
        }, indent=2)
        
    else:
        return json.dumps({
            "topic": "General Caching Overview",
            "summary": f"Query '{query}' returned: Cache-aside minimizes stale data; edge caching minimizes network round-trip distances. Read-heavy 10k req/sec APIs typically require multi-layer caching."
        }, indent=2)


def latency_sla_calculator(strategy: str, req_per_sec: int = 10000, cache_hit_ratio: float = 0.90) -> str:
    """
    Calculate latency percentiles (p50, p95, p99) and origin offload for a given caching strategy and throughput.
    Supports failure simulation to test agentic error handling and adaptation.
    """
    global SIMULATE_TOOL_FAILURE
    
    # Check if failure simulation is triggered
    if SIMULATE_TOOL_FAILURE:
        return json.dumps({
            "error": "ServiceUnavailableError",
            "code": 503,
            "message": "Latency Calculator microservice connection timed out after 3000ms. Downstream dependency unavailable."
        }, indent=2)
        
    strategy_lower = strategy.lower()
    
    if "redis" in strategy_lower:
        p50 = 1.2
        p95 = 3.5
        p99 = 8.0
        network_hop = "VPC internal (1-2ms)"
        origin_load = int(req_per_sec * (1.0 - cache_hit_ratio))
    elif "cdn" in strategy_lower or "edge" in strategy_lower:
        p50 = 18.0
        p95 = 32.0
        p99 = 55.0
        network_hop = "Global Edge Point of Presence (PoP)"
        origin_load = int(req_per_sec * (1.0 - cache_hit_ratio))
    elif "hybrid" in strategy_lower:
        p50 = 2.5
        p95 = 12.0
        p99 = 25.0
        network_hop = "Multi-tier: Edge PoP + Origin VPC Redis"
        origin_load = int(req_per_sec * (1.0 - 0.96))
    else:
        p50 = 45.0
        p95 = 120.0
        p99 = 280.0
        network_hop = "Direct Origin Database"
        origin_load = req_per_sec

    return json.dumps({
        "strategy": strategy,
        "input_rps": req_per_sec,
        "cache_hit_ratio": cache_hit_ratio,
        "network_hop": network_hop,
        "p50_latency_ms": p50,
        "p95_latency_ms": p95,
        "p99_latency_ms": p99,
        "residual_origin_rps": origin_load,
        "sla_assessment": "SLA Compliant (<50ms p95)" if p95 < 50 else "SLA Warning"
    }, indent=2)


def cost_and_resource_estimator(strategy: str, req_per_sec: int = 10000, dataset_size_gb: float = 20.0) -> str:
    """
    Estimate monthly infrastructure cost and compute/memory resource requirements
    for supporting 10k req/sec at specified data volume.
    """
    strategy_lower = strategy.lower()
    monthly_requests_millions = (req_per_sec * 86400 * 30) / 1_000_000 # ~25.9 billion requests
    
    if "redis" in strategy_lower:
        return json.dumps({
            "architecture": "Managed Redis Cluster (Primary + Replica)",
            "memory_required_gb": dataset_size_gb * 1.3, # 30% overhead for buffer/keys
            "estimated_nodes": "3x cache.r6g.xlarge (or equivalent)",
            "monthly_cost_usd": 650.0,
            "cost_breakdown": "Redis instances + inter-VPC networking",
            "pros": "Predictable flat monthly billing regardless of read request spikes",
            "cons": "Origin egress bandwidth still incurs standard cloud provider cost if public"
        }, indent=2)
        
    elif "cdn" in strategy_lower or "edge" in strategy_lower:
        return json.dumps({
            "architecture": "Cloudflare Enterprise / Pro Edge Tier with Workers",
            "edge_requests_handled": f"{monthly_requests_millions:.1f}M req/month",
            "monthly_cost_usd": 280.0,
            "cost_breakdown": "Base CDN subscription + Edge Worker invocations",
            "pros": "Zero egress bandwidth fee; absorbed at the edge",
            "cons": "Extra latency for personalized cache misses; worker CPU limits on complex auth"
        }, indent=2)
        
    elif "hybrid" in strategy_lower:
        return json.dumps({
            "architecture": "Two-Tier: Cloudflare Edge + Smaller Redis Cluster (cache.r6g.large)",
            "monthly_cost_usd": 550.0,
            "cost_breakdown": "Cloudflare CDN ($200) + Redis ($350)",
            "pros": "Optimal balance: lowest origin bandwidth fees + maximum performance for personal data",
            "cons": "Requires maintaining two invalidation pipelines"
        }, indent=2)
        
    else:
        return json.dumps({
            "architecture": "Direct Origin Scaling",
            "monthly_cost_usd": 2400.0,
            "note": "Uncached 10k rps requires massive database read replicas"
        }, indent=2)
