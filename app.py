import streamlit as st
import pandas as pd
import plotly.express as px
import requests

st.set_page_config(
    page_title='Sykes Gems 2026',
    page_icon='💎',
    layout='wide',
    initial_sidebar_state='expanded'
)

st.markdown("""
<style>
@import url("https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=DM+Sans:wght@300;400;500&display=swap");
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
h1, h2, h3 { font-family: 'Playfair Display', serif; }
.stApp { background-color: #0f0f1a; color: #e2e8f0; }
.metric-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 10px;
    padding: 1rem;
    text-align: center;
}
.evidence-quote {
    background: rgba(212,175,55,0.08);
    border-left: 3px solid #d4af37;
    padding: 0.6rem 1rem;
    margin: 0.4rem 0;
    border-radius: 0 8px 8px 0;
    font-style: italic;
    font-size: 0.9rem;
    color: #e2e8f0;
}
.criteria-met { color: #4ade80; font-weight: 500; }
.criteria-review { color: #f59e0b; font-weight: 500; }
.criteria-nodata { color: #94a3b8; font-weight: 500; }
.chat-msg-user {
    background: rgba(212,175,55,0.15);
    border-radius: 12px 12px 2px 12px;
    padding: 0.8rem 1rem;
    margin: 0.5rem 0;
    text-align: right;
}
.chat-msg-ai {
    background: rgba(255,255,255,0.05);
    border-radius: 12px 12px 12px 2px;
    padding: 0.8rem 1rem;
    margin: 0.5rem 0;
}
div[data-testid="stDataFrame"] { border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv('gems_dashboard_data.csv')
    return df

df = load_data()
CATEGORIES = sorted(df['category'].unique().tolist())
COUNTIES   = sorted(df['County'].dropna().unique().tolist())

# API key from Streamlit secrets
API_KEY = st.secrets.get('OPENAI_API_KEY', '')

# ── Header ────────────────────────────────────────────────────────────────────
c1, c2 = st.columns([1, 8])
with c1:
    st.markdown('<div style="font-size:3rem;margin-top:0.5rem">💎</div>', unsafe_allow_html=True)
with c2:
    st.markdown('<h1 style="color:#d4af37;margin-bottom:0">Sykes Gems 2026</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color:#94a3b8;margin-top:0">Award Shortlist · Insight Factory · Sykes Holidays</p>', unsafe_allow_html=True)

st.divider()

tab1, tab2, tab3 = st.tabs(['📊  Overview', '🏡  Shortlist Browser', '💬  Ask the Data'])

# ════════════════════════════════════════════════════════════════════════════
# TAB 1 — OVERVIEW
# ════════════════════════════════════════════════════════════════════════════
with tab1:
    met_n    = int((df['meets_property_criteria'] == True).sum())
    review_n = int((df['meets_property_criteria'] == False).sum())
    nodata_n = int(df['meets_property_criteria'].isna().sum())

    m1, m2, m3, m4 = st.columns(4)
    for col, val, label, color in [
        (m1, len(df), 'Shortlisted properties', '#d4af37'),
        (m2, df['category'].nunique(), 'Award categories', '#d4af37'),
        (m3, met_n, 'Criteria met', '#4ade80'),
        (m4, review_n, 'Manual review', '#f59e0b'),
    ]:
        with col:
            st.markdown(
                f'<div class="metric-card">'
                f'<div style="font-size:2rem;font-weight:700;color:{color}">{val:,}</div>'
                f'<div style="color:#94a3b8;font-size:0.85rem">{label}</div></div>',
                unsafe_allow_html=True
            )

    st.markdown('<br>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)

    with c1:
        st.markdown('### Properties per Category')
        cat_counts = df.groupby(['category', 'meets_property_criteria']).size().reset_index(name='count')
        cat_counts['status'] = cat_counts['meets_property_criteria'].map(
            {True: 'Criteria Met', False: 'Manual Review'}
        ).fillna('No Data')
        fig1 = px.bar(
            cat_counts, x='count', y='category', color='status',
            color_discrete_map={'Criteria Met': '#4ade80', 'Manual Review': '#f59e0b', 'No Data': '#475569'},
            orientation='h', template='plotly_dark'
        )
        fig1.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            legend_title_text='', height=420, margin=dict(l=0, r=0, t=20, b=0)
        )
        st.plotly_chart(fig1, use_container_width=True)

    with c2:
        st.markdown('### Score Distribution by Category')
        fig2 = px.box(
            df, x='property_category_score', y='category',
            template='plotly_dark', color='category',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig2.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False, height=420, margin=dict(l=0, r=0, t=20, b=0)
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('### Top Counties Represented')
    county_counts = df['County'].value_counts().head(15).reset_index()
    county_counts.columns = ['County', 'count']
    fig3 = px.bar(
        county_counts, x='County', y='count', template='plotly_dark',
        color='count', color_continuous_scale=[[0, '#1a1a2e'], [1, '#d4af37']]
    )
    fig3.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False, height=300, margin=dict(l=0, r=0, t=20, b=0),
        coloraxis_showscale=False
    )
    st.plotly_chart(fig3, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 2 — SHORTLIST BROWSER
# ════════════════════════════════════════════════════════════════════════════
with tab2:
    sb1, sb2, sb3, sb4 = st.columns(4)
    with sb1:
        sel_cat = st.selectbox('Category', ['All'] + CATEGORIES)
    with sb2:
        sel_flag = st.selectbox('Criteria status', ['All', 'Criteria met', 'Manual review', 'No data'])
    with sb3:
        sel_county = st.selectbox('County', ['All'] + COUNTIES)
    with sb4:
        sel_ticks = st.selectbox('Min ticks', ['Any', '3+', '4+', '5'])

    filtered = df.copy()
    if sel_cat != 'All':
        filtered = filtered[filtered['category'] == sel_cat]
    if sel_flag == 'Criteria met':
        filtered = filtered[filtered['meets_property_criteria'] == True]
    elif sel_flag == 'Manual review':
        filtered = filtered[filtered['meets_property_criteria'] == False]
    elif sel_flag == 'No data':
        filtered = filtered[filtered['meets_property_criteria'].isna()]
    if sel_county != 'All':
        filtered = filtered[filtered['County'] == sel_county]
    if sel_ticks == '3+':
        filtered = filtered[pd.to_numeric(filtered['SykesTicks'], errors='coerce') >= 3]
    elif sel_ticks == '4+':
        filtered = filtered[pd.to_numeric(filtered['SykesTicks'], errors='coerce') >= 4]
    elif sel_ticks == '5':
        filtered = filtered[pd.to_numeric(filtered['SykesTicks'], errors='coerce') == 5]

    st.markdown(f'**{len(filtered):,} properties** matching filters')

    if len(filtered) > 0:
        prop_options = filtered.apply(
            lambda r: f"{r['property_id']} — {r['PropertyName']} ({r['category']})", axis=1
        ).tolist()
        sel_prop = st.selectbox('Select a property to view detail', prop_options)
        prop_id  = sel_prop.split('—')[0].strip()
        row      = filtered[filtered['property_id'].astype(str) == str(prop_id)].iloc[0]

        st.divider()
        d1, d2, d3 = st.columns([3, 1, 1])
        with d1:
            st.markdown(f"### {row['PropertyName']}")
            st.markdown(
                f"**{row['County']}**, {row['Country']}  ·  "
                f"Category: **{row['category']}**  ·  "
                f"Rank: **#{int(row['category_rank'])}**"
            )
            flag = str(row['criteria_flag'])
            if flag == 'criteria met':
                st.markdown('<span class="criteria-met">✓ Criteria met</span>', unsafe_allow_html=True)
            elif 'manual review' in flag:
                st.markdown(f'<span class="criteria-review">⚠ {flag}</span>', unsafe_allow_html=True)
            else:
                st.markdown(f'<span class="criteria-nodata">○ {flag}</span>', unsafe_allow_html=True)
        with d2:
            score = float(row['property_category_score'])
            st.markdown(
                f'<div class="metric-card">'
                f'<div style="font-size:1.8rem;font-weight:700;color:#d4af37">{score:.2f}</div>'
                f'<div style="color:#94a3b8;font-size:0.8rem">Category score</div></div>',
                unsafe_allow_html=True
            )
        with d3:
            st.markdown(
                f'<div class="metric-card">'
                f'<div style="font-size:1.8rem;font-weight:700;color:#d4af37">{int(row["matching_review_count"])}</div>'
                f'<div style="color:#94a3b8;font-size:0.8rem">Matching reviews</div></div>',
                unsafe_allow_html=True
            )

        a1, a2 = st.columns(2)
        with a1:
            st.markdown('**Property attributes**')
            attr_rows = [
                ('Sleeps', row.get('Sleeps'), None),
                ('Bedrooms', row.get('Bedrooms'), None),
                ('Bathrooms', row.get('Bathrooms'), None),
                ('Ticks', row.get('SykesTicks'), None),
                ('Pets allowed', row.get('AllowsPets'), 1),
                ('Hot tub', row.get('hasHotTub'), 1),
                ('Coastal', row.get('isCoastal'), 1),
                ('Farm', row.get('isFarm'), 1),
                ('Swimming pool', row.get('hasSwimmingPool'), 1),
                ('Child friendly', row.get('isChildFriendly'), 1),
            ]
            for label, val, trueval in attr_rows:
                if trueval is not None:
                    display_val = 'Yes' if val == trueval else 'No'
                else:
                    display_val = val if val is not None else '—'
                st.markdown(f'`{label}` &nbsp; **{display_val}**', unsafe_allow_html=True)

        with a2:
            st.markdown('**Score breakdown**')
            for label, key in [
                ('Bayesian avg match', 'bayesian_avg_match_score'),
                ('Max match score', 'max_match_score'),
                ('Avg sentiment', 'avg_sentiment_score'),
            ]:
                val = row.get(key)
                try:
                    st.markdown(f'`{label}` &nbsp; **{float(val):.2f}**', unsafe_allow_html=True)
                except Exception:
                    st.markdown(f'`{label}` &nbsp; **—**', unsafe_allow_html=True)
            cov = row.get('review_coverage')
            try:
                st.markdown(f'`Review coverage` &nbsp; **{float(cov)*100:.0f}%**', unsafe_allow_html=True)
            except Exception:
                pass

        st.markdown('**Guest review evidence**')
        for i in range(1, 6):
            q = row.get(f'evidence_quote_{i}')
            if q and str(q) not in ['None', 'nan', '']:
                st.markdown(f'<div class="evidence-quote">"{q}"</div>', unsafe_allow_html=True)

        st.divider()
        st.markdown('**All properties matching this filter**')
        display_cols = ['category_rank', 'property_id', 'PropertyName', 'County',
                        'property_category_score', 'matching_review_count', 'SykesTicks', 'criteria_flag']
        available = [c for c in display_cols if c in filtered.columns]
        st.dataframe(
            filtered[available].sort_values(['category', 'category_rank']),
            use_container_width=True, hide_index=True
        )

# ════════════════════════════════════════════════════════════════════════════
# TAB 3 — CHAT
# ════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('### Ask the Gems data')
    st.markdown(
        '<p style="color:#94a3b8">Ask questions about the shortlist in plain English. '
        'The AI has access to all 1,000 shortlisted properties, their scores, attributes and evidence.</p>',
        unsafe_allow_html=True
    )

    if not API_KEY:
        st.warning('OpenAI API key not configured. Add OPENAI_API_KEY to Streamlit secrets to enable chat.')
    else:
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []

        met_n_chat    = int((df['meets_property_criteria'] == True).sum())
        review_n_chat = int((df['meets_property_criteria'] == False).sum())

        st.markdown('**Try asking:**')
        ex_cols = st.columns(3)
        examples = [
            'Which farm stay properties are in Devon?',
            'Show me luxury properties with 5 ticks',
            'Which category has the highest average score?',
            'How many beach properties need manual review?',
            'What evidence do the top 3 pet friendly properties have?',
            'Which counties appear most in the shortlist?'
        ]
        for i, ex in enumerate(examples):
            with ex_cols[i % 3]:
                if st.button(ex, key=f'ex_{i}'):
                    st.session_state.pending_q = ex

        st.divider()

        for msg in st.session_state.chat_history:
            css_class = 'chat-msg-user' if msg['role'] == 'user' else 'chat-msg-ai'
            st.markdown(f'<div class="{css_class}">{msg["content"]}</div>', unsafe_allow_html=True)

        user_q = st.chat_input('Ask anything about the Gems shortlist...')
        if not user_q and 'pending_q' in st.session_state:
            user_q = st.session_state.pop('pending_q')

        if user_q:
            st.session_state.chat_history.append({'role': 'user', 'content': user_q})

            data_context = (
                f"You are a data analyst assistant for the Sykes Gems 2026 award programme at Sykes Holidays. "
                f"Answer questions about the shortlisted properties clearly and concisely. "
                f"When listing properties, include their name, county, score and rank. Use bullet points for lists.\n\n"
                f"SHORTLIST SUMMARY:\n"
                f"- Total properties: {len(df)}\n"
                f"- Categories: {', '.join(CATEGORIES)}\n"
                f"- Properties per category: {df.groupby('category').size().to_dict()}\n"
                f"- Criteria met: {met_n_chat}, Manual review: {review_n_chat}\n"
                f"- Score range: {df['property_category_score'].min():.2f} to {df['property_category_score'].max():.2f}\n"
                f"- Top counties: {df['County'].value_counts().head(10).to_dict()}\n\n"
                f"FULL DATA (first 200 rows):\n"
                f"{df[['property_id','PropertyName','category','category_rank','County','Country','property_category_score','matching_review_count','SykesTicks','meets_property_criteria','criteria_flag','evidence_quote_1','evidence_quote_2']].head(200).to_string()}"
            )

            with st.spinner('Thinking...'):
                try:
                    resp = requests.post(
                        'https://api.openai.com/v1/chat/completions',
                        headers={'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'},
                        json={
                            'model': 'gpt-4o-mini',
                            'messages': [
                                {'role': 'system', 'content': data_context},
                                *[{'role': m['role'], 'content': m['content']}
                                  for m in st.session_state.chat_history]
                            ],
                            'max_tokens': 1000,
                            'temperature': 0.3
                        },
                        timeout=30
                    )
                    answer = resp.json()['choices'][0]['message']['content']
                except Exception as e:
                    answer = f'Error calling AI: {str(e)}'

            st.session_state.chat_history.append({'role': 'assistant', 'content': answer})
            st.rerun()

        if st.button('Clear chat'):
            st.session_state.chat_history = []
            st.rerun()
