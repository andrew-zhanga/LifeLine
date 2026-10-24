import importlib.util,itertools,json
from pathlib import Path
import unittest
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('community',ROOT/'scripts/community/build.py');c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)

class CommunityMath(unittest.TestCase):
    def test_exact_source_tract_group_attribution(self):
        # Three links: source0/cell0=2, source0/cell1=3, source1/cell1=5.
        result=c.attribution(np.array([0,0,1]),np.array([0,1,1]),np.array([2.,3.,5.]),np.array([0,1]),np.array([[10.,20.],[1.,4.],[2.,5.]]),2,2)
        np.testing.assert_array_equal(result[0],[[20,60],[0,100]])
        np.testing.assert_array_equal(result[1],[[2,12],[0,20]])
        np.testing.assert_array_equal(result[2],[[4,15],[0,25]])
        self.assertEqual(result[0].sum(),180.)
        self.assertEqual(result[1].sum(),34.)

    def test_robust_matches_enumerated_max_min(self):
        cost=np.array([2.,2.,3.])*1e6;npv=np.array([3.,2.,4.])*1e6
        seasons=np.array([[.1,.8,.4],[.8,.1,.4]])
        chosen,info=c.robust_solve(cost,npv,seasons,4e6,4e6,5)
        feasible=[np.array(x,dtype=bool) for x in itertools.product([0,1],repeat=3) if cost@x<=4e6 and npv@x>=4e6]
        best=max(seasons[:,x].sum(axis=1).min() for x in feasible)
        self.assertAlmostEqual(seasons[:,chosen].sum(axis=1).min(),best)
        self.assertAlmostEqual(info['minimum_seasonal_reduction_pct'],best*100)
        self.assertEqual(info['solver_status'],'optimal')

    def test_zero_baseline_percent_unknown(self):
        self.assertIsNone(c.metric(0,0)['reduction_pct'])

class ExportChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.community=json.loads((ROOT/'data/build/community/community.json').read_text());cls.robust=json.loads((ROOT/'data/build/community/robustness.json').read_text())
        cls.econ={s['id']:s for s in json.loads((ROOT/'data/build/portfolios/site-economics.json').read_text())['sites']}

    def test_all_plans_reconcile_tracts_and_budget(self):
        for p in self.community['plans']:
            self.assertLessEqual(p['capex_usd'],p['budget_usd']+.01)
            self.assertEqual(len(p['selected_ids']),len(set(p['selected_ids'])))
            self.assertTrue(all(self.econ[i]['eligible_for_capture'] for i in p['selected_ids']))
            self.assertAlmostEqual(p['capex_usd'],sum(self.econ[i]['capex_usd'] for i in p['selected_ids']),places=5)
            for g in self.community['groups']:
                for field in ['baseline','residual','reduction']:
                    self.assertAlmostEqual(p['regional'][g][field],sum(t[g][field] for t in p['tract_results']),places=5)
                self.assertAlmostEqual(p['regional'][g]['baseline'],p['regional'][g]['residual']+p['regional'][g]['reduction'],places=5)

    def test_age_objective_uses_actual_source_counts(self):
        src={x['id']:x for x in json.loads((ROOT/'data/build/exposure/site-benefits.json').read_text())['sites']}
        fields={'population':'annual_population_weighted_index','under5':'under5_weighted_index','age65plus':'age65plus_weighted_index'}
        plans={x['id']:x for x in self.community['plans']}
        for target in self.community['objective_plans']:
            p=plans[target['plan_id']];g=target['group']
            expected=sum(src[i][fields[g]]*.9 for i in p['selected_ids'])
            self.assertAlmostEqual(expected,p['regional'][g]['reduction'],places=6)
            self.assertIn(p['solver_status'],['optimal','feasible_best_found'])

    def test_fixed_plan_price_and_cost_stress_keep_installations(self):
        plans={p['id']:p for p in self.community['plans']}
        annuity=sum(1/1.1**y for y in range(1,8))
        benchmark=next(s['gas_price_usd_per_mmbtu'] for s in self.robust['economic_scenarios'] if s['id']=='benchmark')
        for evaluation in self.robust['fixed_plan_evaluations']:
            p=plans[evaluation['plan_id']];cases={x['scenario_id']:x for x in evaluation['economics']}
            self.assertAlmostEqual(cases['benchmark']['npv_usd'],p['npv_usd'],places=5)
            self.assertAlmostEqual(cases['capex-high']['capex_usd'],p['capex_usd']*1.25,places=5)
            price_delta=p['annual_sellable_mmbtu']*(4-benchmark)*annuity
            self.assertAlmostEqual(cases['price-high']['npv_usd']-p['npv_usd'],price_delta,places=5)
            self.assertEqual(cases['capex-high']['budget_feasible'],cases['capex-high']['capex_usd']<=p['budget_usd']+.01)

    def test_season_reconciliation_and_robust_floor(self):
        sources=self.robust['seasonal_source_benefits'];weather=self.robust['weather_scenarios'];values=np.array(sources['values'])
        annual=np.average(values,axis=0,weights=[w['hours'] for w in weather])
        self.assertEqual(sum(w['hours'] for w in weather),8760)
        self.assertAlmostEqual(sum(annual),self.community['regional_baseline']['population'],places=6)
        lookup={p['plan_id']:p for p in self.robust['fixed_plan_evaluations']}
        for p in self.robust['robust_plans']:
            self.assertGreaterEqual(p['npv_usd']+.01,p['financial_floor_usd'])
            worst=min(w['exposure_reduction_pct'] for w in lookup[p['id']]['weather'])
            self.assertAlmostEqual(worst,p['minimum_seasonal_reduction_pct'])

if __name__=='__main__':unittest.main()
