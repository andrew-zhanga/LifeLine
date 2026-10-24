import importlib.util,json,unittest
from pathlib import Path
import numpy as np
from scipy.integrate import quad
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('transport',ROOT/'scripts/transport/build_transport.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class TransportTests(unittest.TestCase):
    def fixture(self,speed=1,direction=270):
        source=[{'id':'fixture','x_m':0.,'y_m':0.,'z_m':60.,'rate_m3_per_s':2.}]
        receptors=[{'x_m':500.,'y_m':0.,'z_m':0.},{'x_m':-500.,'y_m':0.,'z_m':0.}]
        u,v=m.wind_vectors(speed,direction);vectors=np.tile([u,v],(1,10,1))
        return source,receptors,vectors
    def test_from_direction_cardinals(self):
        for direction,expected in [(0,(0,-1)),(90,(-1,0)),(180,(0,1)),(270,(1,0))]:
            np.testing.assert_allclose(m.wind_vectors(1,direction),expected,atol=1e-14)
    def test_zero_emissions_zero_proxy_and_mass(self):
        s=m.simulate(*self.fixture(),duration=1800,rate_scale=0)
        self.assertFalse(np.array(s['receptor_series']['baseline']).any())
        self.assertEqual(sum(s['mass_budget'][-1]['emitted']),0)
    def test_capture_preserves_old_mass_and_paths(self):
        args=self.fixture();s=m.simulate(*args,duration=3600,install=1200);off=m.simulate(*args,duration=3600,install=1200,capture_fraction=0)
        self.assertEqual(s['frames'],off['frames'])
        for p in s['puffs']:
            self.assertAlmostEqual(p['mass_capture']/p['mass_baseline'],1 if p['birth_elapsed_s']<1200 else .1)
        baseline=np.array(s['receptor_series']['baseline']);capture=np.array(s['receptor_series']['capture'])
        self.assertTrue((capture<=baseline+1e-20).all())
        self.assertGreater(capture[5].sum(),0) # pre-install material still present after capture
    def test_emitted_remaining_exited_and_captured_mass(self):
        s=m.simulate(*self.fixture(speed=20),duration=3600,install=1200,bounds=1000)
        final=s['mass_budget'][-1]
        self.assertGreater(sum(final['exited']),0)
        self.assertAlmostEqual(sum(final['emitted']),2*3600)
        for b in s['mass_budget']:
            np.testing.assert_allclose(b['emitted'],np.array(b['remaining'])+b['exited'],atol=1e-9)
            np.testing.assert_allclose(b['emitted'],np.array(b['capture_remaining'])+b['capture_exited']+b['captured_at_source'],atol=1e-9)
    def test_gaussian_normalizes_and_ground_reflects(self):
        # At x=y=0 divide out known normalized horizontal factor, integrate z>=0.
        center=np.array([[0.,0.,60.]]);sh=np.array([80.]);sv=np.array([50.])
        f=lambda z:float(m.density_at_receptors(center,sh,sv,np.array([[0.,0.,z]]))[0,0])*2*np.pi*80**2
        integral,error=quad(f,0,np.inf,epsabs=1e-10)
        self.assertAlmostEqual(integral,1,places=9)
        derivative=(f(.001)-f(0))/.001
        self.assertAlmostEqual(derivative,0,places=7)
    def test_deterministic_and_timestep_converges(self):
        args=self.fixture();a=m.simulate(*args,duration=1800);b=m.simulate(*args,duration=1800)
        self.assertEqual(a,b)
        fine=m.simulate(*args,duration=1800,dt=30)
        np.testing.assert_allclose(a['receptor_series']['baseline'],fine['receptor_series']['baseline'],atol=1e-20)
    def test_scene_source_ids_timestamps_and_curve_sums(self):
        scene=json.loads((ROOT/'data/build/transport/scene.json').read_text())
        verified=json.loads((ROOT/'data/verified/processed/flares_regional_2023.geojson').read_text())
        ids={s['properties']['id'] for s in verified['features']}
        self.assertTrue(set(s['id'] for s in scene['sources'])<=ids)
        timestamps=np.array([f['timestamp_utc'].removesuffix('Z') for f in scene['frames']],dtype='datetime64[s]')
        self.assertTrue((np.diff(timestamps)==np.timedelta64(300,'s')).all())
        for mode in ['baseline','capture']:
            np.testing.assert_allclose(np.array(scene['receptor_series'][mode+'_per_source']).sum(axis=1),scene['receptor_series'][mode],atol=1e-20)
        diagnostic=json.loads((ROOT/'data/build/transport/diagnostics.json').read_text());self.assertTrue(diagnostic['all_passed'])

if __name__=='__main__':unittest.main()
