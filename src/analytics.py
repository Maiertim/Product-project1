"""Product metrics and user-level randomized experiment calculations."""
import numpy as np
import pandas as pd
from scipy.stats import norm, chi2


def funnel(users: pd.DataFrame) -> pd.DataFrame:
    counts = [len(users), int(users.viewed.sum()), int(users.added_to_cart.sum()), int(users.purchased.sum())]
    return pd.DataFrame({'step': ['Signup', 'View item', 'Add to cart', 'Purchase'],
                         'users': counts, 'from_signup_pct': [100 * n / counts[0] for n in counts]})


def retention(users: pd.DataFrame, events: pd.DataFrame, day: int = 7) -> pd.DataFrame:
    """Exact-day app-open retention (not rolling retention)."""
    activity = events.loc[events.event_name == 'app_open', ['user_id', 'event_date']].drop_duplicates()
    joined = users[['user_id', 'signup_date']].merge(activity, how='left', on='user_id')
    joined['age'] = (pd.to_datetime(joined.event_date) - pd.to_datetime(joined.signup_date)).dt.days
    retained = joined.loc[joined.age == day, 'user_id'].unique()
    cohorts = users.assign(cohort=pd.to_datetime(users.signup_date).dt.to_period('W').astype(str),
                           retained=users.user_id.isin(retained))
    return cohorts.groupby('cohort', as_index=False).agg(users=('user_id', 'size'),
                                                         retained=('retained', 'sum')).assign(
        retention_pct=lambda x: 100 * x.retained / x.users)


def experiment(users: pd.DataFrame) -> dict:
    """Two-sided normal approximation test for user-level purchase conversion."""
    counts = users.groupby('variant').purchased.agg(['sum', 'count'])
    if set(counts.index) != {'control', 'treatment'}:
        raise ValueError('Both control and treatment groups are required')
    xc, nc = int(counts.loc['control', 'sum']), int(counts.loc['control', 'count'])
    xt, nt = int(counts.loc['treatment', 'sum']), int(counts.loc['treatment', 'count'])
    pc, pt = xc / nc, xt / nt
    effect = pt - pc
    pooled = (xc + xt) / (nc + nt)
    pooled_se = np.sqrt(pooled * (1 - pooled) * (1 / nc + 1 / nt))
    z = effect / pooled_se if pooled_se else np.nan
    p_value = float(2 * norm.sf(abs(z))) if pooled_se else np.nan
    se = np.sqrt(pc * (1 - pc) / nc + pt * (1 - pt) / nt)
    ci = (effect - 1.96 * se, effect + 1.96 * se)
    expected = (nc + nt) / 2
    srm_stat = ((nc - expected) ** 2 + (nt - expected) ** 2) / expected
    srm_p = float(chi2.sf(srm_stat, df=1))
    return {'control_n': nc, 'treatment_n': nt, 'control_rate': pc, 'treatment_rate': pt,
            'effect_pp': effect * 100, 'ci_low_pp': ci[0] * 100, 'ci_high_pp': ci[1] * 100,
            'p_value': p_value, 'srm_p_value': srm_p}
