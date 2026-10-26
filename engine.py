"""Explainable rule-based movie recommendation engine. No ML or internet required."""
MOVIES = [
 ('3 Idiots','Comedy','Hindi',2009,8.4,'Family'),('Dangal','Drama','Hindi',2016,8.3,'Family'),
 ('Taare Zameen Par','Drama','Hindi',2007,8.3,'Family'),('Zindagi Na Milegi Dobara','Adventure','Hindi',2011,8.2,'Teen'),
 ('Andhadhun','Thriller','Hindi',2018,8.2,'Adult'),('Drishyam','Thriller','Hindi',2015,8.2,'Teen'),
 ('Chhichhore','Comedy','Hindi',2019,8.3,'Teen'),('Queen','Comedy','Hindi',2013,8.1,'Teen'),
 ('Lagaan','Drama','Hindi',2001,8.1,'Family'),('Kahaani','Thriller','Hindi',2012,8.1,'Teen'),
 ('Interstellar','Sci-Fi','English',2014,8.7,'Teen'),('Inception','Sci-Fi','English',2010,8.8,'Teen'),
 ('The Dark Knight','Action','English',2008,9.0,'Teen'),('The Shawshank Redemption','Drama','English',1994,9.3,'Teen'),
 ('The Pursuit of Happyness','Drama','English',2006,8.0,'Family'),('The Martian','Sci-Fi','English',2015,8.0,'Teen'),
 ('Toy Story','Animation','English',1995,8.3,'Family'),('Finding Nemo','Animation','English',2003,8.2,'Family'),
 ('Inside Out','Animation','English',2015,8.1,'Family'),('Coco','Animation','English',2017,8.4,'Family'),
 ('Spider-Man: Into the Spider-Verse','Animation','English',2018,8.4,'Teen'),
 ('Knives Out','Mystery','English',2019,7.9,'Teen'),('The Grand Budapest Hotel','Comedy','English',2014,8.1,'Teen'),
 ('The Lord of the Rings: The Fellowship of the Ring','Fantasy','English',2001,8.9,'Teen'),
 ('Spirited Away','Animation','Japanese',2001,8.6,'Family'),('Your Name','Romance','Japanese',2016,8.4,'Teen'),
 ('Parasite','Thriller','Korean',2019,8.5,'Adult'),('Train to Busan','Horror','Korean',2016,7.6,'Adult'),
 ('RRR','Action','Telugu',2022,7.8,'Teen'),('Baahubali: The Beginning','Fantasy','Telugu',2015,8.0,'Teen'),
]
CATALOG = [dict(title=t,genre=g,language=l,year=y,rating=r,audience=a) for t,g,l,y,r,a in MOVIES]
AUDIENCE_ALLOWED = {'Family': {'Family'}, 'Teen': {'Family','Teen'}, 'Adult': {'Family','Teen','Adult'}}

def forward_chain(preferences):
    """Derive user facts from inputs; returns inferred facts and fired production rules."""
    facts, trace = set(), []
    def fire(rule, fact):
        if fact not in facts:
            facts.add(fact); trace.append(f'{rule}: inferred {fact}')
    genre = preferences.get('genre','Any')
    mood = preferences.get('mood','Any')
    mood_map = {'Laugh':'Comedy','Excited':'Action','Curious':'Mystery','Inspired':'Drama','Imaginative':'Sci-Fi'}
    if genre != 'Any': fire('R1 genre selection', f'preferred_genre:{genre}')
    if mood in mood_map and genre == 'Any': fire('R2 mood mapping', f'preferred_genre:{mood_map[mood]}')
    if preferences.get('language','Any') != 'Any': fire('R3 language selection', f"preferred_language:{preferences['language']}")
    if preferences.get('era','Any') != 'Any': fire('R4 release period', f"preferred_era:{preferences['era']}")
    return facts, trace

def backward_verify(movie, preferences):
    """Prove recommend(movie) by checking every mandatory prerequisite."""
    checks = []
    def check(rule, condition, message):
        checks.append((rule, bool(condition), message))
    audience = preferences.get('audience','Adult')
    check('R5 audience safety', movie['audience'] in AUDIENCE_ALLOWED[audience], f"{movie['audience']} category allowed for {audience} audience")
    min_rating = float(preferences.get('min_rating',0))
    check('R6 minimum rating', movie['rating'] >= min_rating, f"Rating {movie['rating']} >= {min_rating}")
    return all(item[1] for item in checks), checks

def recommend(preferences, limit=10):
    facts, forward_trace = forward_chain(preferences)
    inferred_genre = next((x.split(':',1)[1] for x in facts if x.startswith('preferred_genre:')),None)
    results, rejected = [], []
    for movie in CATALOG:
        eligible, checks = backward_verify(movie, preferences)
        if not eligible:
            rejected.append({'title':movie['title'],'failed_rules':[reason for _,ok,reason in checks if not ok]})
            continue
        matches, weights = [], []
        def add(label, condition, weight):
            weights.append(weight)
            if condition: matches.append((label,weight))
        if inferred_genre: add('Genre',movie['genre']==inferred_genre,40)
        language = preferences.get('language','Any')
        if language!='Any': add('Language',movie['language']==language,25)
        era = preferences.get('era','Any')
        if era!='Any': add('Release period', (movie['year']>=2015 if era=='2015 onwards' else movie['year']<2015),20)
        # A small rating component is always active; it breaks ties for otherwise matching items.
        matches.append(('IMDb-style catalogue rating',15*movie['rating']/10)); weights.append(15)
        score = round(100*sum(w for _,w in matches)/sum(weights),1)
        reasons = [name for name,_ in matches if name!='IMDb-style catalogue rating']
        if not reasons: reasons=['Meets all mandatory conditions']
        results.append({**movie,'score':score,'reasons':reasons,'checks':checks})
    results.sort(key=lambda x:(-x['score'],-x['rating'],x['title']))
    return {'recommended':results[:limit],'eligible_count':len(results),'rejected':rejected,
            'facts':sorted(facts),'forward_trace':forward_trace}

if __name__=='__main__':
    sample={'genre':'Sci-Fi','mood':'Any','language':'English','era':'2015 onwards','audience':'Teen','min_rating':8.0}
    for m in recommend(sample,5)['recommended']: print(f"{m['title']}: {m['score']}% ({', '.join(m['reasons'])})")
