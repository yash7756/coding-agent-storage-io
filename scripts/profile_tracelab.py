
import duckdb

DB_PATH = "datasets/raw/syfi_coding_trace.duckdb"

con = duckdb.connect(DB_PATH, read_only=True)

print("\n========== 1. DATASET SIZE ==========")

query = """
SELECT
    COUNT(*) AS total_rounds,
    COUNT(DISTINCT session_id) AS unique_sessions,
    COUNT(DISTINCT project) AS unique_projects,
    COUNT(DISTINCT model) AS unique_models
FROM rounds
"""

print(con.execute(query).fetchdf().to_string(index=False))

query = """
SELECT
    COUNT(*) AS total_tool_calls,
    COUNT(DISTINCT tool_name) AS unique_tool_names,
    SUM(CASE WHEN command_skeleton IS NOT NULL THEN 1 ELSE 0 END)
        AS calls_with_command_skeleton,
    SUM(CASE WHEN executables IS NOT NULL THEN 1 ELSE 0 END)
        AS calls_with_executables,
    SUM(CASE WHEN tool_wall_latency_ms IS NOT NULL THEN 1 ELSE 0 END)
        AS calls_with_timing
FROM tool_calls
"""

print("\n========== 2. TOOL CALL COVERAGE ==========")
print(con.execute(query).fetchdf().to_string(index=False))

print("\n========== 3. TOOL FREQUENCY ==========")

query = """
SELECT
    tool_name,
    COUNT(*) AS total_calls,
    ROUND(AVG(tool_wall_latency_ms), 2) AS avg_latency_ms,
    SUM(CASE WHEN is_error = TRUE THEN 1 ELSE 0 END) AS errors
FROM tool_calls
GROUP BY tool_name
ORDER BY total_calls DESC
"""

print(con.execute(query).fetchdf().to_string(index=False))

print("\n========== 4. COMMAND PARSING STATUS ==========")

query = """
SELECT
    executable_parse_status,
    COUNT(*) AS total_calls
FROM tool_calls
GROUP BY executable_parse_status
ORDER BY total_calls DESC
"""

print(con.execute(query).fetchdf().to_string(index=False))

print("\n========== 5. EVENT TYPES ==========")

query = """
SELECT
    event_type,
    COUNT(*) AS total_events
FROM timing_events
GROUP BY event_type
ORDER BY total_events DESC
"""

print(con.execute(query).fetchdf().to_string(index=False))

print("\n========== 6. TIMESTAMP COVERAGE ==========")

query = """
SELECT
    MIN(timestamp) AS first_event,
    MAX(timestamp) AS last_event,
    COUNT(*) AS total_events
FROM timing_events
"""

print(con.execute(query).fetchdf().to_string(index=False))

con.close()

print("\nTraceLab profiling completed.")
