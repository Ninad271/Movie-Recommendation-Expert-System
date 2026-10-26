import streamlit as st
from engine import CATALOG, recommend
st.set_page_config(page_title='Movie Recommendation Expert System', page_icon='🎬', layout='wide')
st.title('🎬 Movie Recommendation Expert System')
st.caption('Explainable symbolic AI • IF–THEN rules • Forward and backward chaining • Offline knowledge base')
st.info('Choose your preferences. This is a rule-based academic prototype, not a trained machine-learning model.')
with st.sidebar:
    st.header('Your preferences')
    genre=st.selectbox('Favorite genre',['Any']+sorted({m['genre'] for m in CATALOG}))
    mood=st.selectbox('Mood',['Any','Laugh','Excited','Curious','Inspired','Imaginative'])
    language=st.selectbox('Language',['Any']+sorted({m['language'] for m in CATALOG}))
    era=st.selectbox('Release period',['Any','Before 2015','2015 onwards'])
    audience=st.selectbox('Audience restriction (mandatory)',['Family','Teen','Adult'],index=2)
    min_rating=st.slider('Minimum catalogue rating (mandatory)',0.0,10.0,7.5,0.1)
    count=st.slider('Maximum recommendations',1,15,8)
    run=st.button('Recommend movies',type='primary',use_container_width=True)
if run:
    choices={'genre':genre,'mood':mood,'language':language,'era':era,'audience':audience,'min_rating':min_rating}
    outcome=recommend(choices,count)
    c1,c2,c3=st.columns(3)
    c1.metric('Catalogue titles',len(CATALOG)); c2.metric('Eligible',outcome['eligible_count']); c3.metric('Rejected',len(outcome['rejected']))
    st.subheader('Recommended movies')
    if not outcome['recommended']:
        st.warning('No movie satisfies all mandatory constraints. Try a lower minimum rating or a broader audience category.')
    for rank,movie in enumerate(outcome['recommended'],1):
        with st.container(border=True):
            st.markdown(f"**{rank}. {movie['title']}** — {movie['score']}% preference match")
            st.write(f"{movie['genre']} · {movie['language']} · {movie['year']} · Catalogue rating {movie['rating']}/10 · {movie['audience']}")
            st.caption('Why: '+', '.join(movie['reasons']))
            with st.expander('Backward-chaining proof'):
                for rule,passed,reason in movie['checks']: st.write(('✅' if passed else '❌')+f' {rule}: {reason}')
    with st.expander('AI reasoning: forward chaining and inferred facts'):
        st.write('Initial preferences:',choices)
        st.write('Inferred facts:',outcome['facts'] or 'No additional preference facts')
        for line in outcome['forward_trace']: st.write('• '+line)
    with st.expander('Rejected movies and reasons'):
        for item in outcome['rejected']: st.write(f"**{item['title']}**: "+'; '.join(item['failed_rules']))
else:
    st.write('Select preferences in the sidebar and click **Recommend movies** to view results and the rule trace.')
st.divider()
st.caption('Ratings and audience tags are illustrative catalogue metadata, not live verified classifications. Scores indicate rule alignment, not probability of enjoyment.')
