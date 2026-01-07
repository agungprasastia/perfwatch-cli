"""
AI Prompts - Prompt templates for AI analysis.
"""

PERFORMANCE_ANALYSIS_PROMPT = """You are a web performance expert analyzing test results.

Given the following performance data, provide a detailed analysis:

{data}

Include:
1. Summary of current performance state
2. Identified bottlenecks
3. Specific recommendations with priority
4. Expected improvements if recommendations are followed
"""

SEO_ANALYSIS_PROMPT = """You are an SEO expert analyzing website optimization.

Given the following SEO data:

{data}

Provide:
1. SEO health summary
2. Critical issues that need immediate attention
3. Optimization opportunities
4. Technical SEO recommendations
"""

LOAD_TEST_ANALYSIS_PROMPT = """You are a backend performance expert analyzing load test results.

Given the following load test data:

{data}

Analyze:
1. Server capacity assessment
2. Response time patterns
3. Error rate analysis
4. Scaling recommendations
5. Bottleneck identification
"""

COMPREHENSIVE_REPORT_PROMPT = """Generate a comprehensive performance report for stakeholders.

URL: {url}
Test Date: {date}

Performance Data:
{performance_data}

SEO Data:
{seo_data}

Load Test Data:
{load_test_data}

Create a professional report including:
1. Executive Summary
2. Key Metrics Overview
3. Detailed Findings
4. Recommendations (prioritized)
5. Action Items with timeline
"""
