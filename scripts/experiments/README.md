# Industrial smoke segmentation research

This additive experiment uses Mommert et al., *Characterization of Industrial Smoke Plumes from Remote Sensing Data* (NeurIPS climate workshop, 2020), https://zenodo.org/records/4250706 and https://github.com/HSG-AIML/IndustrialSmokePlumes.

This is European industrial-smoke imagery from 2019, not a verified gas-flare dataset. Predicted masks do not measure emissions, concentrations or health outcomes and do not validate the Texas transport model. Original authors' published scores are not our scores.

## Reproduce

Install `requirements.txt` into `.data-venv` alongside existing build requirements. Download `segmentation_labels.tar.gz` from the Zenodo record and extract JSON files into `data/experiments/industrial-smoke/labels`. Run:

```
.data-venv/bin/python scripts/experiments/download_smoke.py
.data-venv/bin/python scripts/experiments/train_smoke.py --epochs 24
```

The downloader uses eight resumable byte ranges and verifies the published imagery MD5. Raw data is ignored by Git. The preparer selects all images with manual segmentation polygons and a deterministic approximately 5% sample of published negative-class images (treated as empty masks). Label Studio percentage coordinates are multiplied by 1.2 for 120×120 pixels, as specified by the dataset. Inputs use 12 bands, excluding B10, with fixed reflectance scaling.

All imagery from a site belongs to one split, determined by a fixed SHA256 rule: ~60% sites train,20% validation,20% test. Model checkpoint and output threshold selected only by validation IoU. The held-out test is evaluated after selection. A simple bright-neutral RGB baseline is tuned on validation and evaluated on the same held-out test. Small U-Net trained from scratch; no external checkpoint download or hidden pretrained weights.

Outputs: `data/build/experiments/{split.json,training-history.json,results.json,examples/,checkpoints/unet-best.pt}`. The final small checkpoint is included explicitly; intermediate checkpoints and raw imagery are ignored. SHA256 is recorded. Examples show lowest, median and highest test IoU, not cherry-picked successes. Metrics are micro-aggregated foreground IoU/Dice/precision/recall; background-dominated pixel accuracy is not a headline.

An Apple MPS synthetic throughput benchmark is recorded separately; it is neither a training nor evaluation result. Exact GPU reproducibility can vary by software/hardware version. The experiment is research, not a replication of the paper or validation on gas flares.

Dataset license: Creative Commons Attribution 4.0 (CC BY 4.0), verified from Zenodo record metadata. Credit: Michael Mommert, Mario Sigel, Marcel Neuhausler, Linus Scheibenreif, Damian Borth; contains modified Copernicus Sentinel data (2019), processed by ESA. Rendered research examples are transformed RGB/mask comparisons, not original unmodified imagery.

Band ordering was checked against the upstream loader: Sentinel-2 B10 is GeoTIFF band 11 (zero-based index 10), because B8A precedes B9. Smaller edge tiles are edge-padded to 120×120, larger ones cropped; masks remain in the published coordinate frame. Rasterization uses PIL polygon fill rather than the source paper's all-touched rasterizer, so boundary pixels can differ. Training adds horizontal/vertical flips to inputs and masks together.

Independent review added exact label-coverage and unique-stem assertions, preprocessing-cache fingerprint invalidation, and a geographic leakage audit. Site IDs with overlapping observed WGS84 footprint envelopes are joined before assigning split hashes, so nearby duplicate facility IDs cannot cross splits. Only118–120pixel edge dimensions are accepted and explicitly recorded; unexpected shapes fail. Report pixel-micro foreground metrics with class counts: the chosen positive/negative sampling prevalence is not deployment prevalence. The model receives12bands whereas the deliberately simple RGB heuristic receives3; this comparison is not an isolated architecture ablation.

## Completed bounded run

24epochs on Apple MPS, checkpoint selected at epoch21 by validation IoU; output threshold0.4 selected on validation. 2,314images:1,433train,507validation,374test. A geographic overlap audit merged458site IDs into439disjoint location groups before splitting. Test:162positive and212negative images across94location groups.

Held-out foreground pixel-micro IoU: U-Net0.47117 versus RGB heuristic0.23554. U-Net Dice0.64054, precision0.62708, recall0.65459. These are research-set metrics, not deployment precision or health measurements. End-to-end preparation+training run230seconds after imagery download. One malformed1-point polygon was omitted; the affected image retains three valid polygons. Two119-pixel-wide tiles were edge-padded; all other2,312images were120×120.

The final small model checkpoint is explicitly included in Git at `data/build/experiments/checkpoints/unet-best.pt` despite the generic checkpoint-directory ignore rule; no raw imagery is committed. Verify published numbers and generate training/evaluation figure with `report_smoke.py`. Checkpoint SHA256 is recorded in results.json.
