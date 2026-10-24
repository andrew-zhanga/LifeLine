"""Independent consequential economics and integer-program checks."""
import importlib.util
import itertools
from pathlib import Path
import unittest
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('portfolio',ROOT/'scripts/portfolio/build.py')
build=importlib.util.module_from_spec(spec); spec.loader.exec_module(build)

class PortfolioTests(unittest.TestCase):
    def setUp(self):
        self.p=build.read(ROOT/'contracts/parameters.json')

    def test_hand_calculation_and_no_capex_double_count(self):
        # Synthetic volume gives exactly 100 recovered Mcf/day; distance zero.
        volume=100*365*1000/(self.p['capture_fraction']*self.p['ft3_per_m3'])
        value=build.economics(volume,0,2,self.p)
        capex=375000
        energy=100*365*1.1*.95
        margin=energy*1.5-capex*.03
        expected=-capex+margin*sum(1/1.1**year for year in range(1,8))
        self.assertAlmostEqual(value['capex_usd'],capex)
        self.assertAlmostEqual(value['annual_sellable_mmbtu'],energy)
        self.assertAlmostEqual(value['npv_usd'],expected)
        self.assertAlmostEqual(value['payback_years'],capex/margin)

    def test_nonpositive_margin_has_null_payback(self):
        for price in [0,.5]:
            value=build.economics(1e6,1,price,self.p)
            self.assertLess(value['annual_margin_usd'],0)
            self.assertIsNone(value['payback_years'])
            self.assertTrue(value['payback_reason'])
        value=build.economics(0,0,0,{**self.p,'annual_fixed_opex_fraction':0})
        self.assertEqual(value['annual_margin_usd'],0)
        self.assertIsNone(value['payback_years'])

    def test_milp_matches_exhaustive_selection(self):
        cost=np.array([4,3,2,5])*1e6
        npv=np.array([8,4,-2,7])*1e6
        benefit=np.array([2,5,9,6.])
        budget=7e6
        selections=[np.array(x,dtype=bool) for x in itertools.product([0,1],repeat=4)]
        feasible=[x for x in selections if sum(cost[x])<=budget]
        for objective,minimum in [('financial',None),('exposure',None),('exposure',7e6)]:
            chosen,info=build.solve(cost,npv,benefit,budget,objective,minimum)
            values=npv if objective=='financial' else benefit
            valid=[x for x in feasible if minimum is None or sum(npv[x])>=minimum]
            self.assertAlmostEqual(sum(values[chosen]),max(sum(values[x]) for x in valid))
            self.assertEqual(info['solver_status'],'optimal')

    def test_negative_financial_can_select_empty(self):
        chosen,_=build.solve([1e6,2e6],[-1e6,-2e6],[1,2],3e6,'financial')
        self.assertEqual(len(chosen),0)

    def test_buffer_excluded_and_balanced_disabled(self):
        sites=[dict(id='eligible',eligible_for_capture=True,annual_flared_m3=100.,pipeline_distance_km=1.), dict(id='buffer',eligible_for_capture=False,annual_flared_m3=1e8,pipeline_distance_km=0.)]
        result=build.make_scenario(sites,{'eligible':1.,'buffer':100.},101.,2e6,0.,self.p,'test',frontier=False)
        plans={x['preset']:x for x in result['plans']}
        self.assertEqual(plans['Financial']['selected_ids'],[])
        self.assertTrue(plans['Balanced']['disabled_reason'])
        self.assertEqual(plans['Exposure']['selected_ids'],['eligible'])
        self.assertAlmostEqual(plans['Exposure']['exposure_reduction_pct'],.9/101*100)

    def test_decline_lowers_npv_without_changing_initial_capex(self):
        a=build.economics(1e7,1,2.5,self.p)
        b=build.economics(1e7,1,2.5,self.p,decline=.15)
        self.assertEqual(a['capex_usd'],b['capex_usd'])
        self.assertLess(b['npv_usd'],a['npv_usd'])

if __name__=='__main__':unittest.main()
