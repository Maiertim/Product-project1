"""ProductProject1 MVP dashboard."""
from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.express as px
from src.analytics import funnel, retention, experiment
from src.generate_data import generate

st.set_page_config(page_title='ProductProject1', page_icon='📈', layout='wide')
st.title('ProductProject1')
st.caption('Synthetic marketplace • Product analytics decision workspace • MVP 0.1')

@st.cache_data
def load_data():
    root = Path(__file__).resolve().parent / 'data'
    if (root / 'users.csv').exists() and (root / 'events.csv').exists():
        users = pd.read_csv(root / 'users.csv', parse_dates=['signup_date'])
        events = pd.read_csv(root / 'events.csv', parse_dates=['event_date'])
    else:
        users, events = generate()
    return users, events

users, events = load_data()
with st.sidebar:
    st.header('Filters')
    platform = st.multiselect('Platform', sorted(users.platform.unique()), default=sorted(users.platform.unique()))
    region = st.multiselect('Region', sorted(users.region.unique()), default=sorted(users.region.unique()))
    st.info('All data is synthetic. No customer information or actual experiment results.')
filtered = users[users.platform.isin(platform) & users.region.isin(region)].copy()
filtered_events = events[events.user_id.isin(filtered.user_id)]
if filtered.empty:
    st.warning('Select at least one platform and one region.')
    st.stop()

k1, k2, k3, k4 = st.columns(4)
k1.metric('Users', f'{len(filtered):,}')
k2.metric('Buyers', f'{filtered.purchased.sum():,}')
k3.metric('Purchase conversion', f'{filtered.purchased.mean():.1%}')
k4.metric('Revenue', f'{filtered.revenue.sum():,.0f} ₽')

tab1, tab2, tab3 = st.tabs(['Conversion funnel', 'Cohort retention', 'A/B testing'])
with tab1:
    f = funnel(filtered)
    st.plotly_chart(px.bar(f, x='step', y='users', text='from_signup_pct',
                           title='Users at each funnel step'), use_container_width=True)
    st.dataframe(f, use_container_width=True, hide_index=True)
    st.caption('Steps are ordered flags in the synthetic generator; not a general event-sequence attribution model.')
with tab2:
    day = st.selectbox('Exact retention day', [1, 7, 30], index=1)
    cohorts = retention(filtered, filtered_events, day)
    st.plotly_chart(px.line(cohorts, x='cohort', y='retention_pct', markers=True,
                            title=f'D{day} exact-day retention by signup week'), use_container_width=True)
    st.dataframe(cohorts, use_container_width=True, hide_index=True)
    st.caption('All generated cohorts have complete D30 observation in this synthetic dataset.')
with tab3:
    st.subheader('Randomized experiment: purchase conversion')
    result = experiment(filtered)
    a, b, c = st.columns(3)
    a.metric('Control', f"{result['control_rate']:.2%}", f"n={result['control_n']:,}")
    b.metric('Treatment', f"{result['treatment_rate']:.2%}", f"n={result['treatment_n']:,}")
    c.metric('Difference', f"{result['effect_pp']:+.2f} pp")
    st.write(f"95% confidence interval (Wald): **[{result['ci_low_pp']:.2f}, {result['ci_high_pp']:.2f}] pp**")
    st.write(f"Two-sided z-test p-value: **{result['p_value']:.4g}**")
    st.write(f"SRM chi-square p-value (expected 50/50): **{result['srm_p_value']:.4g}**")
    if result['srm_p_value'] < 0.01:
        st.error('Potential sample-ratio mismatch. Check assignment and exposure tracking before interpreting impact.')
    else:
        st.info('No SRM detected at the 1% threshold. This does not establish experiment validity.')
    st.caption('Exploratory tests on a synthetic user-level randomization. Filters may change the estimand; do not infer causality from arbitrary post-treatment segments.')

st.divider()
st.subheader('Next: AI analyst')
st.write('Planned: natural-language questions → validated SQL/metrics → evidence-backed hypotheses, not fabricated causal claims.')
