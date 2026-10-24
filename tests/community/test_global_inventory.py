import importlib.util,json,unittest
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('global_inventory',ROOT/'scripts/community/global_inventory.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
class GlobalInventory(unittest.TestCase):
    def test_antimeridian_center_and_bounds(self):
        center,bounds=g.geometry_summary([[179,0],[-179,0]],[1,1])
        self.assertAlmostEqual(abs(center[0]),180)
        self.assertAlmostEqual(bounds[2]-bounds[0],2)
    def test_global_country_reconciliation_and_flags(self):
        data=json.loads((ROOT/'data/build/community/global-inventory.json').read_text())
        self.assertEqual(sum(c['site_count'] for c in data['countries']),8783)
        self.assertAlmostEqual(sum(c['annual_flared_m3'] for c in data['countries'])/1e9,data['annual_flared_m3']/1e9,places=9)
        self.assertTrue(all(not c['available_analysis']['economics'] for c in data['countries']))
        self.assertTrue(all(np.isfinite(c['center']+c['bounds']).all() for c in data['countries']))
        self.assertEqual(len(data['regions']),1)
        self.assertTrue(data['regions'][0]['available_analysis']['annual_screening'])
if __name__=='__main__':unittest.main()
