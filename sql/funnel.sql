-- DuckDB SQL. Unique users at ordered funnel steps.
SELECT 'signup' AS step, COUNT(*) AS users FROM read_csv_auto('data/users.csv')
UNION ALL
SELECT 'view_item', COUNT(*) FROM read_csv_auto('data/users.csv') WHERE viewed
UNION ALL
SELECT 'add_to_cart', COUNT(*) FROM read_csv_auto('data/users.csv') WHERE added_to_cart
UNION ALL
SELECT 'purchase', COUNT(*) FROM read_csv_auto('data/users.csv') WHERE purchased;
