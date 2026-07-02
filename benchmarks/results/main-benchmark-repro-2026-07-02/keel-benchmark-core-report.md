# Keel Benchmark Core Report

This round of benchmarking is narrowed to just four layers - harness regression, context ablation, working memory ablation, and recovery ablation - and does not fold in any other conclusions from provider, run aggregation, or durable memory.

## Harness Regression
- Fixed regression task count: 12
- pass_rate: 100.00%
- within_budget_rate: 100.00%
- verifier_pass_rate: 100.00%

## Context Ablation
- Config count: 12
- avg_full_prompt_chars: 5575.67
- avg_raw_prompt_chars: 6994.33
- avg_prompt_compression_ratio: 16.36%
- max_prompt_compression_ratio: 33.59%
- current_request_preserved_rate: 100.00%

## Working Memory Ablation
- memory_on repeated_reads: 0
- memory_off repeated_reads: 60
- memory_on avg_tool_steps: 0.00
- memory_on correct_rate: 100.00%
- memory_hit_rate: 100.00%

## Recovery / Resume Ablation
- resume_success_rate: 90.00%
- stale_reanchor_rate: 100.00%
- workspace_drift_detection_rate: 100.00%
- resume_false_accept_rate: 0.00%

## Headline Metrics
- avg_full_prompt_chars
- avg_raw_prompt_chars
- avg_prompt_compression_ratio
- max_prompt_compression_ratio
- repeated_reads
- avg_tool_steps
- correct_rate
- resume_success_rate
- workspace_drift_detection_rate
- resume_false_accept_rate

## Supplementary Metrics
- current_request_preserved_rate
- memory_hit_rate
- stale_reanchor_rate
- failure_category_counts

## Scope boundaries
- Harness regression only proves the runtime contract is stable; it does not prove the provider ceiling.
- The context, memory, and recovery layers only prove per-module gains; they are not mixed with provider benchmarks.
