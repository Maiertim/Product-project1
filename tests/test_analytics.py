import pytest
from src.generate_data import generate
from src.analytics import funnel, retention, experiment

@pytest.fixture(scope='module')
def sample():
    return generate(n_users=1000, seed=7)

def test_funnel_monotonic(sample):
    result = funnel(sample[0])
    assert result.users.is_monotonic_decreasing
    assert result.users.iloc[0] == 1000

def test_retention_bounds(sample):
    result = retention(*sample, day=7)
    assert result.retention_pct.between(0, 100).all()
    assert result.retained.le(result.users).all()

def test_experiment(sample):
    result = experiment(sample[0])
    assert result['control_n'] + result['treatment_n'] == 1000
    assert 0 <= result['p_value'] <= 1
    assert 0 <= result['srm_p_value'] <= 1
    assert result['ci_low_pp'] <= result['effect_pp'] <= result['ci_high_pp']
