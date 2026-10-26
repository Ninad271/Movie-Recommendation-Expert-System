import unittest
from engine import CATALOG, forward_chain, backward_verify, recommend
class EngineTests(unittest.TestCase):
    def test_catalogue(self): self.assertGreaterEqual(len(CATALOG),30)
    def test_forward_mood(self): self.assertIn('preferred_genre:Comedy',forward_chain({'genre':'Any','mood':'Laugh'})[0])
    def test_explicit_genre_overrides_mood(self): self.assertIn('preferred_genre:Drama',forward_chain({'genre':'Drama','mood':'Laugh'})[0])
    def test_rating_hard_constraint(self): self.assertTrue(all(m['rating']>=8.5 for m in recommend({'min_rating':8.5})['recommended']))
    def test_family_hard_constraint(self): self.assertTrue(all(m['audience']=='Family' for m in recommend({'audience':'Family'})['recommended']))
    def test_no_match(self): self.assertEqual(recommend({'min_rating':10})['eligible_count'],0)
    def test_backward_explanation(self):
        eligible,trace=backward_verify(CATALOG[0],{'audience':'Family','min_rating':9})
        self.assertFalse(eligible); self.assertTrue(any(not ok for _,ok,_ in trace))
    def test_score_range(self): self.assertTrue(all(0<=m['score']<=100 for m in recommend({})['recommended']))
if __name__=='__main__': unittest.main()
