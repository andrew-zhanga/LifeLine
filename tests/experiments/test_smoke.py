import sys,unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts/experiments'))
from train_smoke import split,metrics,UNet
import torch
class SmokeChecks(unittest.TestCase):
 def test_site_split_stable(self):
  self.assertEqual(split('12345'),split('12345'))
  self.assertEqual(set(split(str(i)) for i in range(1000)),{'train','validation','test'})
 def test_foreground_metrics(self):
  r=metrics(np.array([1,1,0,0]),np.array([1,0,1,0]))
  self.assertAlmostEqual(r['iou'],1/3);self.assertAlmostEqual(r['dice'],.5)
 def test_network_spatial_output_and_gradients(self):
  m=UNet();x=torch.rand(2,12,120,120);y=m(x)
  self.assertEqual(tuple(y.shape),(2,1,120,120));y.mean().backward()
  self.assertTrue(all(p.grad is not None and torch.isfinite(p.grad).all() for p in m.parameters()))
if __name__=='__main__':unittest.main()
