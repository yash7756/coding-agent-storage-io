import duckdb

DB_PATH = "datasets/raw/syfi_coding_trace.duckdb"

con = duckdb.connect(DB_PATH, read_only=True)

print("=" * 75)
print("TOOL CALL RELATIONSHIP VALIDATION")
print("=" * 75)

query = """
SELECT
    COUNT(*) AS total_timing_events,

    COUNT(tool_call_id) AS events_with_nonnull_tool_id,

    COUNT(*) FILTER (
        WHERE tool_call_id IS NOT NULL
          AND TRIM(tool_call_id) <> ''
    ) AS events_with_nonempty_tool_id,

    COUNT(DISTINCT tool_call_id) AS distinct_tool_call_ids,

    COUNT(*) FILTER (
        WHERE tool_call_id IS NOT NULL
          AND EXISTS (
              SELECT 1
              FROM tool_calls t
              WHERE t.tool_call_id = e.tool_call_id
          )
    ) AS globally_matched,

    COUNT(*) FILTER (
        WHERE tool_call_id IS NOT NULL
          AND EXISTS (
              SELECT 1
              FROM tool_calls t
              WHERE t.round_pk = e.round_pk
                AND t.tool_call_id = e.tool_call_id
          )
    ) AS composite_matched,

    COUNT(*) FILTER (
        WHERE tool_call_id IS NOT NULL
          AND NOT EXISTS (
              SELECT 1
              FROM tool_calls t
              WHERE t.round_pk = e.round_pk
                AND t.tool_call_id = e.tool_call_id
          )
    ) AS composite_unmatched,

    COUNT(*) FILTER (
        WHERE tool_call_id IS NOT NULL
          AND EXISTS (
              SELECT 1
              FROM tool_calls t
              WHERE t.tool_call_id = e.tool_call_id
          )
          AND NOT EXISTS (
              SELECT 1
              FROM tool_calls t
              WHERE t.round_pk = e.round_pk
                AND t.tool_call_id = e.tool_call_id
          )
    ) AS matched_globally_but_not_in_same_round

FROM timing_events e;
"""

print(con.execute(query).fetchdf().to_string(index=False))

print("\n" + "=" * 75)
print("UNMATCHED EVENTS BY EVENT TYPE")
print("=" * 75)

query = """
SELECT
    e.event_type,
    COUNT(*) AS unmatched_event_count,
    COUNT(DISTINCT e.tool_call_id) AS distinct_unmatched_ids
FROM timing_events e
WHERE e.tool_call_id IS NOT NULL
  AND NOT EXISTS (
      SELECT 1
      FROM tool_calls t
      WHERE t.round_pk = e.round_pk
        AND t.tool_call_id = e.tool_call_id
  )
GROUP BY e.event_type
ORDER BY unmatched_event_count DESC;
"""

print(con.execute(query).fetchdf().to_string(index=False))

print("\n" + "=" * 75)
print("SAMPLE UNMATCHED EVENTS")
print("=" * 75)

query = """
SELECT
    e.round_pk,
    e.event_index,
    e.event_type,
    e.tool_call_id,
    e.tool_name,
    e.source
FROM timing_events e
WHERE e.tool_call_id IS NOT NULL
  AND NOT EXISTS (
      SELECT 1
      FROM tool_calls t
      WHERE t.round_pk = e.round_pk
        AND t.tool_call_id = e.tool_call_id
  )
ORDER BY e.round_pk
LIMIT 15;
"""

print(con.execute(query).fetchdf().to_string(index=False))

con.close()

print("\nValidation completed.")