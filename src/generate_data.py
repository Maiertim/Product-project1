"""Reproducible synthetic marketplace data. Not real customer records."""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def generate(n_users: int = 8000, seed: int = 42):
    rng = np.random.default_rng(seed)
    user_id = np.arange(1, n_users + 1)
    signup = pd.Timestamp('2026-01-01') + pd.to_timedelta(rng.integers(0, 60, n_users), unit='D')
    variant = rng.choice(['control', 'treatment'], size=n_users)
    platform = rng.choice(['ios', 'android', 'web'], size=n_users, p=[.34, .46, .20])
    region = rng.choice(['Moscow', 'Saint Petersburg', 'Other'], size=n_users, p=[.35, .20, .45])
    viewed = rng.random(n_users) < .84
    cart = viewed & (rng.random(n_users) < .43)
    # A simulated positive treatment effect; never interpret as real-world evidence.
    conversion_prob = np.where(variant == 'treatment', .43, .35)
    purchased = cart & (rng.random(n_users) < conversion_prob)
    revenue = np.where(purchased, rng.integers(500, 8500, n_users), 0)
    users = pd.DataFrame({'user_id': user_id, 'signup_date': signup, 'variant': variant,
                          'platform': platform, 'region': region, 'viewed': viewed,
                          'added_to_cart': cart, 'purchased': purchased, 'revenue': revenue})
    rows = []
    for u in users.itertuples(index=False):
        rows.append((u.user_id, u.signup_date, 'signup'))
        if u.viewed:
            rows.append((u.user_id, u.signup_date + pd.Timedelta(days=1), 'view_item'))
        if u.added_to_cart:
            rows.append((u.user_id, u.signup_date + pd.Timedelta(days=2), 'add_to_cart'))
        if u.purchased:
            rows.append((u.user_id, u.signup_date + pd.Timedelta(days=3), 'purchase'))
        # Returning activity is independent of treatment in this synthetic example.
        for day, probability in [(1, .46), (7, .25), (30, .12)]:
            if rng.random() < probability:
                rows.append((u.user_id, u.signup_date + pd.Timedelta(days=day), 'app_open'))
    events = pd.DataFrame(rows, columns=['user_id', 'event_date', 'event_name'])
    return users, events


def save_data():
    users, events = generate()
    path = ROOT / 'data'
    path.mkdir(exist_ok=True)
    users.to_csv(path / 'users.csv', index=False)
    events.to_csv(path / 'events.csv', index=False)
    print(f'Saved {len(users):,} users and {len(events):,} events')


if __name__ == '__main__':
    save_data()
