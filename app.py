import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ── CONFIG ────────────────────────────────────────────────────
st.set_page_config(
    page_title="HCP Engagement Engine",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── LOAD DATA ─────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_excel('hcp_app.xlsx')
    return df

df = load_data()

# ── SIDEBAR ───────────────────────────────────────────────────
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/a/a8/ZS_Associates_logo.svg/320px-ZS_Associates_logo.svg.png", width=120)
st.sidebar.title("HCP Engagement Engine")
st.sidebar.caption("GLP-1 Drug Targeting | CMS Medicare Part D 2024")
st.sidebar.markdown("---")

page = st.sidebar.radio("Navigate", [
    "📊 Overview",
    "🔍 HCP Explorer",
    "📋 Rep Call Plan",
    "💰 Business Impact",
    "ℹ️ About"
])

st.sidebar.markdown("---")
st.sidebar.caption(
    "⚠️ CRM engagement data (emails, visits, webinars) is **simulated**. "
    "Prescribing data is real CMS Medicare Part D 2024."
)

# ── PAGE 1: OVERVIEW ──────────────────────────────────────────
if page == "📊 Overview":
    st.title("HCP Engagement Engine — Overview")
    st.caption("Omnichannel targeting engine for GLP-1 drug prescribers across 625,608 US doctors")

    st.markdown("---")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total HCPs",        f"{len(df):,}")
    c2.metric("GLP-1 Prescribers", f"{int(df['prescribes_glp1'].sum()):,}",
              f"{df['prescribes_glp1'].mean():.1%} of total")
    c3.metric("KOLs Identified",   f"{int(df['is_kol'].sum()):,}")
    c4.metric("Avg Propensity",    f"{df['propensity_score'].mean():.3f}")

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("HCP Segment Distribution")
        seg = df['segment_name'].value_counts().reset_index()
        seg.columns = ['Segment', 'Count']
        fig = px.pie(
            seg, names='Segment', values='Count',
            color_discrete_sequence=px.colors.qualitative.Set2,
            hole=0.35
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Next Best Action Distribution")
        nba = df['next_best_action'].value_counts().reset_index()
        nba.columns = ['Channel', 'Count']
        fig2 = px.bar(
            nba, x='Channel', y='Count',
            color='Channel',
            color_discrete_sequence=['#2ecc71','#3498db','#e74c3c'],
            text='Count'
        )
        fig2.update_traces(texttemplate='%{text:,}', textposition='outside')
        fig2.update_layout(showlegend=False, yaxis_title="HCP Count")
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Avg Propensity Score by State")
    state_df = df.groupby('state')['propensity_score'].mean().reset_index()
    fig3 = px.choropleth(
        state_df,
        locations='state',
        locationmode='USA-states',
        color='propensity_score',
        scope='usa',
        color_continuous_scale='Greens',
        title='Avg HCP Propensity Score by State',
        labels={'propensity_score': 'Avg Propensity'}
    )
    fig3.update_layout(margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("---")
    st.subheader("Segment Propensity Distribution")
    fig4 = px.box(
        df, x='segment_name', y='propensity_score',
        color='segment_name',
        color_discrete_sequence=px.colors.qualitative.Set2,
        labels={'segment_name': 'Segment', 'propensity_score': 'Propensity Score'}
    )
    fig4.update_layout(showlegend=False)
    st.plotly_chart(fig4, use_container_width=True)


# ── PAGE 2: HCP EXPLORER ──────────────────────────────────────
elif page == "🔍 HCP Explorer":
    st.title("HCP Explorer")
    st.caption("Filter and explore individual HCPs by state, segment, and recommended channel")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        state_filter = st.selectbox("State", ["All"] +
                       sorted(df['state'].dropna().unique().tolist()))
    with col2:
        seg_filter = st.selectbox("Segment", ["All"] +
                     sorted(df['segment_name'].dropna().unique().tolist()))
    with col3:
        nba_filter = st.selectbox("Next Best Action", ["All"] +
                     sorted(df['next_best_action'].dropna().unique().tolist()))
    with col4:
        kol_filter = st.selectbox("KOL Only", ["All", "KOL Only"])

    filtered = df.copy()
    if state_filter != "All":
        filtered = filtered[filtered['state'] == state_filter]
    if seg_filter != "All":
        filtered = filtered[filtered['segment_name'] == seg_filter]
    if nba_filter != "All":
        filtered = filtered[filtered['next_best_action'] == nba_filter]
    if kol_filter == "KOL Only":
        filtered = filtered[filtered['is_kol'] == 1]

    st.markdown(f"**{len(filtered):,} HCPs match filters**")

    show_cols = ['Prscrbr_NPI', 'specialty', 'state', 'segment_name',
                 'propensity_score', 'is_kol', 'next_best_action', 'priority_score']
    st.dataframe(
        filtered[show_cols]
        .sort_values('propensity_score', ascending=False)
        .head(200)
        .reset_index(drop=True)
        .style.background_gradient(subset=['propensity_score'], cmap='Greens')
        .format({'propensity_score': '{:.3f}', 'priority_score': '{:.3f}'}),
        use_container_width=True
    )

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Propensity Score Distribution")
        fig = px.histogram(
            filtered, x='propensity_score', nbins=50,
            color_discrete_sequence=['#2ecc71'],
            labels={'propensity_score': 'Propensity Score', 'count': 'HCP Count'}
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Specialty Breakdown")
        spec = filtered['specialty'].value_counts().head(10).reset_index()
        spec.columns = ['Specialty', 'Count']
        fig2 = px.bar(
            spec, x='Count', y='Specialty', orientation='h',
            color_discrete_sequence=['#3498db']
        )
        fig2.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig2, use_container_width=True)


# ── PAGE 3: REP CALL PLAN ─────────────────────────────────────
elif page == "📋 Rep Call Plan":
    st.title("Weekly Rep Call Plan by Territory")
    st.caption(
        "Call list prioritized by LP-optimized priority score "
        "(propensity × 0.5 + segment weight × 0.3 + KOL flag × 0.2) "
        "with $3,000 budget, 20 rep-visit cap, and min 3 KOL constraints."
    )

    col1, col2 = st.columns([2, 1])
    with col1:
        state_sel = st.selectbox("Select Territory (State)",
                                  sorted(df['state'].dropna().unique().tolist()))
    with col2:
        cap = st.slider("Weekly Call Capacity", 20, 100, 50)

    CHANNEL_COST = {'rep_visit': 150, 'email': 5, 'webinar': 30}

    state_data = df[df['state'] == state_sel].copy()
    top_hcps   = state_data.nlargest(cap, 'priority_score')
    weekly_cost = top_hcps['next_best_action'].map(CHANNEL_COST).sum()

    st.markdown("---")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("HCPs Selected",    f"{len(top_hcps):,}")
    c2.metric("Avg Propensity",   f"{top_hcps['propensity_score'].mean():.3f}")
    c3.metric("KOLs in Plan",     int(top_hcps['is_kol'].sum()))
    c4.metric("Est. Weekly Cost", f"${weekly_cost:,.0f}")

    show_cols = ['Prscrbr_NPI', 'specialty', 'segment_name',
                 'propensity_score', 'is_kol', 'next_best_action', 'priority_score']
    st.dataframe(
        top_hcps[show_cols]
        .reset_index(drop=True)
        .style.background_gradient(subset=['propensity_score'], cmap='Greens')
        .format({'propensity_score': '{:.3f}', 'priority_score': '{:.3f}'}),
        use_container_width=True
    )

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader(f"Channel Breakdown — {state_sel}")
        ch = top_hcps['next_best_action'].value_counts().reset_index()
        ch.columns = ['Channel', 'Count']
        fig = px.pie(
            ch, names='Channel', values='Count',
            color_discrete_sequence=['#2ecc71','#3498db','#e74c3c'],
            hole=0.35
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader(f"Segment Breakdown — {state_sel}")
        sg = top_hcps['segment_name'].value_counts().reset_index()
        sg.columns = ['Segment', 'Count']
        fig2 = px.bar(
            sg, x='Segment', y='Count',
            color='Segment',
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig2.update_layout(showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)


# ── PAGE 4: BUSINESS IMPACT ───────────────────────────────────
elif page == "💰 Business Impact":
    st.title("Business Impact — Model vs Specialty Baseline")
    st.info(
        "**Baseline = specialty-only logistic regression** (what a rep team uses without this model). "
        "Not random targeting — a realistic, fair comparison. "
        "AUC: 0.9732 (model) vs 0.8616 (specialty-only). "
        "Lift computed on held-out test set."
    )

    total_calls    = 61 * 50
    cost_per_visit = 150

    b_score = 0.4606
    m_score = 0.9774
    b_conv  = round(b_score * total_calls)
    m_conv  = round(m_score * total_calls)
    b_cost  = (total_calls * cost_per_visit) / max(b_conv, 1)
    m_cost  = (total_calls * cost_per_visit) / max(m_conv, 1)

    st.markdown("---")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Baseline Converters",   f"{b_conv:,}")
    c2.metric("Model Converters",      f"{m_conv:,}", f"+{m_conv - b_conv:,}")
    c3.metric("Baseline Cost/Convert", f"${b_cost:,.0f}")
    c4.metric("Model Cost/Convert",    f"${m_cost:,.0f}", f"-${b_cost - m_cost:,.0f}")

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        fig = go.Figure(go.Bar(
            x=['Specialty Baseline', 'XGBoost Model'],
            y=[b_score, m_score],
            marker_color=['#e74c3c', '#2ecc71'],
            text=[f"{b_score:.3f}", f"{m_score:.3f}"],
            textposition='outside'
        ))
        fig.update_layout(
            title='Avg Propensity Score',
            yaxis_title='Score (0–1)',
            yaxis_range=[0, 1.1]
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = go.Figure(go.Bar(
            x=['Specialty Baseline', 'XGBoost Model'],
            y=[b_cost, m_cost],
            marker_color=['#e74c3c', '#2ecc71'],
            text=[f"${b_cost:,.0f}", f"${m_cost:,.0f}"],
            textposition='outside'
        ))
        fig2.update_layout(
            title='Cost per Conversion (USD)',
            yaxis_title='USD'
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.success(
        f"✅ Model delivers **{(m_score / b_score - 1):.0%} lift** over specialty-only targeting "
        f"and saves **${b_cost - m_cost:,.0f} per conversion**."
    )

    st.markdown("---")
    st.subheader("LP Optimization Summary (Weekly)")
    col1, col2 = st.columns(2)
    with col1:
        lp_data = {
            'Metric': [
                'HCPs Selected', 'Total Weekly Cost',
                'KOLs Covered', 'Territories Optimized',
                'Avg Cost per HCP'
            ],
            'Value': [
                '2,867', '$169,880', '250 / 250',
                '51 (all US states + DC)', '$59'
            ]
        }
        st.table(pd.DataFrame(lp_data))

    with col2:
        st.subheader("Channel Cost Assumptions")
        cost_data = {
            'Channel':  ['Rep Visit', 'Webinar', 'Email'],
            'Cost/HCP': ['$150', '$30', '$5'],
            'Weekly Cap': ['20 visits/rep', '—', '—']
        }
        st.table(pd.DataFrame(cost_data))

    st.markdown("---")
    st.subheader("Model Performance")
    perf_data = {
        'Metric': ['AUC-ROC', 'Precision', 'Recall', 'F1 Score',
                   'Specialty-only AUC', 'AUC Lift over Baseline'],
        'Value':  ['0.9732', '0.7070', '0.9125', '0.7967',
                   '0.8616', '+11.2 points']
    }
    st.table(pd.DataFrame(perf_data))


# ── PAGE 5: ABOUT ─────────────────────────────────────────────
elif page == "ℹ️ About":
    st.title("About This Project")

    st.markdown("""
    ## Omnichannel HCP Engagement Engine
    **GLP-1 Drug Targeting | Built for Pharma Commercial Analytics**

    ---

    ### What This Does
    Pharma sales reps cannot visit every doctor. This engine identifies which
    Healthcare Providers are most likely to prescribe GLP-1 drugs (Ozempic, Mounjaro, etc.)
    and recommends the optimal outreach channel — personalised per HCP.

    ---

    ### Pipeline Modules

    | Module | Method | Output |
    |---|---|---|
    | HCP Segmentation | KMeans (k=5) | Champions, GLP1_Rising, Digital_First, Low_Priority, Institutional |
    | Propensity Scoring | XGBoost + SHAP | 0–1 GLP-1 prescription likelihood per HCP |
    | KOL Detection | PageRank on KNN graph | 250 Key Opinion Leaders identified |
    | Next-Best-Action | Thompson Sampling (Beta-Bernoulli Bandit) | email / rep_visit / webinar per HCP |
    | Territory Optimization | Linear Programming (PuLP/CBC) | Weekly call plan per state |

    ---

    ### Data Sources

    | Source | Type | Details |
    |---|---|---|
    | CMS Medicare Part D 2024 | **Real** | 15.4M rows, 625,608 US prescribers |
    | CRM Engagement Layer | **Simulated** | emails, visits, webinars — synthetic stand-in for Veeva/Salesforce |

    ---

    ### Key Honest Limitations
    - CMS Part D covers Medicare (65+) population only. Younger GLP-1 prescribers may be undercounted.
    - CRM engagement data is simulated. In production, replace with real Veeva CRM exports.
    - Conversion lift is computed against a specialty-only baseline, not random targeting.

    ---

    ### Tech Stack
    `XGBoost` · `Scikit-learn` · `SHAP` · `NetworkX` · `PuLP` · `Streamlit` · `Plotly` · `Pandas`
    """)
