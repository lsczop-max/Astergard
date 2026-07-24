WITH legacy_rows AS (
  SELECT p.username
  FROM players AS p
  WHERE json_valid(p.effects_json)
    AND json_type(p.effects_json) = 'array'
    AND EXISTS (
      SELECT 1
      FROM json_each(p.effects_json) AS e
      WHERE COALESCE(json_type(e.value, '$.value') = 'integer', 0)
        AND (
          (
            json_extract(e.value, '$.name') = 'Wzmocnienie'
            AND json_extract(e.value, '$.modifier_stat') = 'sila'
            AND json_extract(e.value, '$.value') = 4
          )
          OR (
            json_extract(e.value, '$.name') = 'Odrzut Źródła'
            AND json_extract(e.value, '$.modifier_stat') = 'sila_woli'
            AND json_extract(e.value, '$.value') = -2
          )
        )
    )
)
UPDATE players
SET effects_json = (
  SELECT COALESCE(json_group_array(json(kept.value)), '[]')
  FROM (
    SELECT e.key, e.value
    FROM json_each(players.effects_json) AS e
    WHERE NOT (
      COALESCE(json_type(e.value, '$.value') = 'integer', 0)
      AND (
        (
          json_extract(e.value, '$.name') = 'Wzmocnienie'
          AND json_extract(e.value, '$.modifier_stat') = 'sila'
          AND json_extract(e.value, '$.value') = 4
        )
        OR (
          json_extract(e.value, '$.name') = 'Odrzut Źródła'
          AND json_extract(e.value, '$.modifier_stat') = 'sila_woli'
          AND json_extract(e.value, '$.value') = -2
        )
      )
    )
    ORDER BY CAST(e.key AS INTEGER)
  ) AS kept
)
WHERE username IN (SELECT username FROM legacy_rows);
