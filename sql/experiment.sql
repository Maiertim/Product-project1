-- Analysis at unit of randomization: user; avoids event-row inflation.
SELECT variant, COUNT(*) AS users,
       SUM(CAST(purchased AS INTEGER)) AS buyers,
       AVG(CAST(purchased AS INTEGER)) AS conversion_rate,
       SUM(revenue) AS revenue
FROM read_csv_auto('data/users.csv')
GROUP BY variant
ORDER BY variant;
