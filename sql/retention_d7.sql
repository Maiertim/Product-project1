-- D7 exact-day return by weekly signup cohort, using each user once.
WITH users AS (
  SELECT user_id, CAST(signup_date AS DATE) AS signup_date
  FROM read_csv_auto('data/users.csv')
), opens AS (
  SELECT DISTINCT user_id, CAST(event_date AS DATE) AS event_date
  FROM read_csv_auto('data/events.csv')
  WHERE event_name = 'app_open'
), user_retention AS (
  SELECT u.user_id, DATE_TRUNC('week', u.signup_date) AS cohort,
         MAX(CASE WHEN DATE_DIFF('day', u.signup_date, o.event_date) = 7 THEN 1 ELSE 0 END) AS returned_d7
  FROM users u LEFT JOIN opens o ON u.user_id = o.user_id
  GROUP BY u.user_id, DATE_TRUNC('week', u.signup_date)
)
SELECT cohort, COUNT(*) AS users, SUM(returned_d7) AS returned_d7,
       AVG(returned_d7) AS retention_d7
FROM user_retention
GROUP BY cohort
ORDER BY cohort;
