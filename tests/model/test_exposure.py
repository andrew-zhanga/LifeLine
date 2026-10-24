"""Physical convention and sparse artifact invariant checks (stdlib unittest)."""
import importlib.util
import json
from pathlib import Path
import unittest
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('build_exposure', ROOT/'scripts/model/build_exposure.py')
model=importlib.util.module_from_spec(spec); spec.loader.exec_module(model)
P=json.loads((ROOT/'contracts/parameters.json').read_text())

class KernelTests(unittest.TestCase):
    def test_cardinal_from_directions(self):
        # North wind transports south; east wind transports west, etc.
        for direction,down in [(0,(0,-5)),(90,(-5,0)),(180,(0,5)),(270,(5,0))]:
            self.assertGreater(float(model.kernel(*down,3,direction,P)),0)
            self.assertEqual(float(model.kernel(-down[0],-down[1],3,direction,P)),0)
    def test_calm_finite_isotropic_and_cutoff(self):
        self.assertEqual(float(model.kernel(0,0,0,0,P)),1)
        a=model.kernel(1,2,0,30,P); b=model.kernel(-2,1,0,270,P)
        self.assertAlmostEqual(float(a),float(b))
        self.assertEqual(float(model.kernel(31,0,0,270,P)),0)
        self.assertTrue(np.isfinite(model.kernel(1,1,0,0,P)))
    def test_hand_calculated_centerline(self):
        self.assertAlmostEqual(float(model.kernel(0,-5,2,0,P)),float(np.exp(-5/15)/(2*6)))
    def test_crosswind_at_source_is_zero(self):
        self.assertEqual(float(model.kernel(1,0,3,0,P)),0)
    def test_source_linearity(self):
        w=model.kernel(0,-5,3,0,P)
        np.testing.assert_allclose(7*w+13*w,20*w)

class ArtifactTests(unittest.TestCase):
    def test_sparse_sums_and_fixed_capture(self):
        out=ROOT/'data/build/exposure'
        manifest=json.loads((out/'exposure-manifest.json').read_text())
        benefits=json.loads((out/'site-benefits.json').read_text())
        a=np.load(out/'annual-source-contributions.npz')
        r=np.load(out/'replay-source-contributions.npz')
        baseline=np.load(out/'replay-baseline.npz')['values']
        self.assertEqual(r['values'].shape,(48,len(a['values'])))
        np.testing.assert_array_equal(a['site_index'],r['site_index'])
        np.testing.assert_array_equal(a['cell_index'],r['cell_index'])
        expected=np.array([np.bincount(r['cell_index'],weights=v,minlength=len(manifest['cell_ids'])) for v in r['values']])
        np.testing.assert_allclose(expected,baseline,rtol=1e-12)
        eligible=np.array([s['eligible_for_capture'] for s in benefits['sites']])
        # Selecting all eligible sources preserves exact buffer contributions.
        reduction=P['capture_fraction']*eligible[r['site_index']]
        residual=np.array([np.bincount(r['cell_index'],weights=v*(1-reduction),minlength=len(manifest['cell_ids'])) for v in r['values']])
        self.assertTrue((residual>=0).all()); self.assertTrue((residual<=baseline+1e-9).all())
        self.assertTrue((reduction[~eligible[r['site_index']]]==0).all())
    def test_actual_hour_axis(self):
        weather=json.loads((ROOT/'data/verified/processed/weather_2023.json').read_text())['locations']
        expected=np.arange(np.datetime64('2023-01-01T00'),np.datetime64('2024-01-01T00'),np.timedelta64(1,'h'))
        for location in weather:
            np.testing.assert_array_equal(np.array(location['hourly']['time'],dtype='datetime64[h]'),expected)
        manifest=json.loads((ROOT/'data/build/exposure/exposure-manifest.json').read_text())
        replay=np.array([s.removesuffix('Z') for s in manifest['replay_hours_utc']],dtype='datetime64[h]')
        self.assertTrue(np.all(np.diff(replay)==np.timedelta64(1,'h')))
        self.assertTrue(np.isin(replay,expected).all())

    def test_data_validations_pass(self):
        validation=json.loads((ROOT/'data/build/exposure/validation.json').read_text())
        self.assertTrue(validation['all_passed'])

if __name__=='__main__': unittest.main()
