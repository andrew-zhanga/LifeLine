"""Reproducible sparse annual relative-exposure screening, not a dispersion model.
Run: .data-venv/bin/python scripts/model/build_exposure.py
"""
from pathlib import Path
import hashlib
import json
import time
import resource
import numpy as np
from scipy.spatial import cKDTree
from pyproj import Transformer

ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT / 'data/verified/processed'
OUT = ROOT / 'data/build/exposure'
PARAM = ROOT / 'contracts/parameters.json'


def kernel(dx, dy, speed, direction, p):
    """Broadcastable inputs, km distances, m/s speed, meteorological FROM degrees."""
    angle = np.deg2rad(direction)
    east, north = -np.sin(angle), -np.cos(angle)
    x, y = dx * east + dy * north, dx * north - dy * east
    xp = np.maximum(x, 0)
    ordinary = np.exp(-0.5 * (y / (p['kernel_width_base_km'] + p['kernel_width_slope'] * xp)) ** 2)
    ordinary *= np.exp(-xp / p['kernel_decay_km']) / (np.maximum(speed, p['calm_threshold_mps']) * (1 + xp))
    ordinary = np.where(x > 0, ordinary, 0)
    value = np.where(speed < p['calm_threshold_mps'], np.exp(-(dx * dx + dy * dy) / 8), ordinary)
    return np.where(dx * dx + dy * dy <= p['cutoff_km'] ** 2, value, 0)


def read(name):
    return json.loads((INPUT / name).read_text())


def projected(coords):
    c = np.asarray(coords)
    x, y = Transformer.from_crs(4326, 32614, always_xy=True).transform(c[:, 0], c[:, 1])
    return np.column_stack([x, y]) / 1000


def main():
    started = time.perf_counter()
    OUT.mkdir(parents=True, exist_ok=True)
    p = json.loads(PARAM.read_text())
    filenames = ['flares_regional_2023.geojson', 'population_receptors.geojson', 'population_grid.geojson', 'population_tracts.geojson', 'weather_2023.json']
    provenance = [{'path': 'data/verified/processed/' + n, 'sha256': hashlib.sha256((INPUT / n).read_bytes()).hexdigest()} for n in filenames]
    provenance.append({'path': 'contracts/parameters.json', 'sha256': hashlib.sha256(PARAM.read_bytes()).hexdigest()})
    meta = {'schema_version': '1.0', 'model_version': 'screening-v1', 'provenance': provenance}
    def write(name, obj):
        (OUT / name).write_text(json.dumps({**meta, **obj}, allow_nan=False, separators=(',', ':')) + '\n')
    sites = read(filenames[0])['features']
    cells = read(filenames[1])['features']
    grid = read(filenames[2])['features']
    tracts = read(filenames[3])['features']
    weather = read(filenames[4])['locations']
    site_ids = [s['properties']['id'] for s in sites]
    cell_ids = [c['properties']['id'] for c in cells]
    assert cell_ids == [c['properties']['id'] for c in grid]
    source_xy = projected([s['geometry']['coordinates'] for s in sites])
    cell_xy = projected([c['geometry']['coordinates'] for c in cells])
    weather_xy = projected([[w['longitude'], w['latitude']] for w in weather])
    weather_distance, assignment = cKDTree(weather_xy).query(source_xy)
    near = cKDTree(cell_xy).query_ball_point(source_xy, p['cutoff_km'])
    si = np.repeat(np.arange(len(sites)), [len(n) for n in near]).astype(np.int32)
    ci = np.concatenate([np.sort(n) for n in near]).astype(np.int32)
    delta = cell_xy[ci] - source_xy[si]
    dx, dy = delta.T
    rate = np.array([s['properties']['annual_flared_m3'] for s in sites]) / 8760
    pop = np.array([[c['properties'][k] for c in cells] for k in ['population', 'under5', 'age65plus']])
    times = weather[0]['hourly']['time']
    assert len(times) == 8760 and len(set(times)) == 8760
    for w in weather:
        assert w['hourly']['time'] == times
        assert w['units']['wind_speed_100m'] == 'm/s', w['units']
    speeds = np.array([w['hourly']['wind_speed_100m'] for w in weather])
    directions = np.array([w['hourly']['wind_direction_100m'] for w in weather])
    assert np.isfinite(speeds).all() and np.isfinite(directions).all()
    # Choose among UTC-midnight starts: maximum circular direction variation
    # over the mesh, excluding near-calm hours; independent of portfolio outcomes.
    candidates = np.arange(0, len(times) - 47, 24)
    scores = []
    for start in candidates:
        theta = np.deg2rad(directions[:, start:start+48])
        moving = speeds[:, start:start+48] >= p['calm_threshold_mps']
        circular = np.abs(np.sum(np.exp(1j * theta) * moving, axis=1) / np.maximum(moving.sum(axis=1), 1))
        scores.append(float(np.mean(1 - circular)))
    replay_start = int(candidates[np.argmax(scores)])
    replay_idx = np.arange(replay_start, replay_start + 48)
    replay_times = [times[i] + ':00Z' for i in replay_idx]
    def contributions(indices, height=100):
        sp = np.array([w['hourly'][f'wind_speed_{height}m'] for w in weather])[:, indices]
        dr = np.array([w['hourly'][f'wind_direction_{height}m'] for w in weather])[:, indices]
        return kernel(dx[None, :], dy[None, :], sp[assignment[si]].T, dr[assignment[si]].T, p) * rate[si][None, :]
    first = contributions(replay_idx[:1])[0]
    first_cells = np.bincount(ci, weights=first, minlength=len(cells))
    write('early-frame.json', {'cell_ids': cell_ids, 'values': first_cells.tolist(), 'timestamp_utc': replay_times[0]})
    coverage = {'analysis_mode': 'full_hourly_year', 'year': 2023, 'hours': 8760, 'expected_hours': 8760, 'coverage_fraction': 1, 'time_start_utc': times[0]+':00Z', 'time_end_utc': times[-1]+':00Z', 'aggregation': 'arithmetic mean of all hourly source contributions', 'wind_height_m': 100}
    manifest = {'site_ids': site_ids, 'cell_ids': cell_ids, 'weather_ids': [w['id'] for w in weather], 'site_weather_ids': [weather[a]['id'] for a in assignment], 'replay_hours_utc': replay_times, 'analysis_coverage': coverage, 'parameters': p, 'units': {'cell_index': 'relative source-volume-weighted index', 'population_weighted_index': 'relative index × allocated residents', 'source_strength': 'annual m³ / 8760; constant m³/hour proxy', 'distance': 'km in EPSG:32614'}, 'replay_selection': {'criterion': 'maximum mean circular direction variation across nine locations among UTC-midnight 48h windows, excluding calm directions; independent of intervention outcomes', 'score': max(scores)}, 'limitations': ['Relative screening index, not pollutant concentration, personal exposure or health risk.', 'Annual satellite-estimated gas volume implies constant activity; no pollutant factor or hourly operation observations.', 'Uniform tract-area population allocation in prepared 5 km cells; not observed home locations.', 'Nine coarse ERA5 weather locations; nearest location assigned in EPSG:32614.', 'Calm winds below 0.5 m/s use an isotropic screening convention with uncertain direction.', '30 km cutoff, finite source domain and uncalibrated kernel omit transport beyond study sources.', 'Wind vectors use meteorological true east/north directions directly on UTM coordinates; local grid convergence is not corrected.']}
    write('exposure-manifest.json', manifest)
    trial_start = time.perf_counter()
    trial = contributions(np.arange(48))
    trial_seconds = time.perf_counter() - trial_start
    print(json.dumps({'early_frame': replay_times[0], 'sparse_links': len(si), 'trial_48h_seconds': trial_seconds, 'projected_year_seconds': trial_seconds * 8760 / 48}), flush=True)
    annual_sum = trial.sum(axis=0)
    annual_start = time.perf_counter()
    for start in range(48, 8760, 96):
        annual_sum += contributions(np.arange(start, min(start + 96, 8760))).sum(axis=0)
    annual_seconds = time.perf_counter() - annual_start
    annual = annual_sum / 8760
    baseline = np.bincount(ci, weights=annual, minlength=len(cells))
    benefits = np.array([np.bincount(si, weights=annual * weight[ci], minlength=len(sites)) for weight in pop])
    total = float(baseline @ pop[0])
    write('annual-baseline.json', {'cell_ids': cell_ids, 'values': baseline.tolist(), 'population_weighted_index': total})
    write('site-benefits.json', {'sites': [{'id': site_ids[i], 'eligible_for_capture': bool(s['properties']['eligible_for_capture']), 'annual_population_weighted_index': float(benefits[0,i]), 'under5_weighted_index': float(benefits[1,i]), 'age65plus_weighted_index': float(benefits[2,i])} for i,s in enumerate(sites)], 'baseline_population_weighted_index': total})
    npmeta = {'schema_version': np.array('1.0'), 'model_version': np.array('screening-v1'), 'provenance_json': np.array(json.dumps(provenance))}
    np.savez_compressed(OUT/'annual-source-contributions.npz', site_index=si, cell_index=ci, values=annual, **npmeta)
    replay = contributions(replay_idx)
    replay_baseline = np.array([np.bincount(ci, weights=row, minlength=len(cells)) for row in replay])
    np.savez_compressed(OUT/'replay-source-contributions.npz', site_index=si, cell_index=ci, values=replay, **npmeta)
    np.savez_compressed(OUT/'replay-baseline.npz', values=replay_baseline, **npmeta)
    # Bounded, explicitly sampled height sensitivity: first 00,06,12,18 UTC each month.
    sensitivity_idx = np.array([i for i,t in enumerate(times) if t[8:10] == '01' and t[11:13] in ['00','06','12','18']])
    sens100 = contributions(sensitivity_idx).mean(axis=0)
    sens10 = contributions(sensitivity_idx, 10).mean(axis=0)
    sens_total100 = float(sens100 @ pop[0,ci]); sens_total10 = float(sens10 @ pop[0,ci])
    eligible = np.array([s['properties']['eligible_for_capture'] for s in sites])
    selected = np.flatnonzero(eligible)[:20]
    fraction = np.where(np.isin(si, selected), p['capture_fraction'], 0)
    residual = np.array([np.bincount(ci, weights=row * (1-fraction), minlength=len(cells)) for row in replay])
    tract_map = {t['properties']['geoid']: t['properties'] for t in tracts}
    errors = []
    for k in ['population','under5','age65plus']:
        allocated = {}
        for c in cells:
            props = c['properties']; allocated[props['geoid']] = allocated.get(props['geoid'], 0) + props[k]
        errors += [abs(v - tract_map[g][k]) for g,v in allocated.items()]
    checks = {'finite_nonnegative_outputs': bool(np.isfinite(replay).all() and (replay >= 0).all() and np.isfinite(annual).all() and (annual >= 0).all()), 'site_cell_ordering_identical': cell_ids == [c['properties']['id'] for c in grid], 'source_benefits_sum_to_baseline': bool(np.isclose(benefits[0].sum(), total, rtol=1e-12)), 'capture_never_raises_index': bool((residual <= replay_baseline + 1e-9).all()), 'no_negative_residuals': bool((residual >= 0).all()), 'buffer_sources_unchanged': bool((fraction[~eligible[si]] == 0).all()), 'population_conserved_by_tract_all_age_groups': max(errors) < 1e-7, 'source_rate_integrates_to_annual_volume': bool(np.allclose(rate*8760, [s['properties']['annual_flared_m3'] for s in sites])), 'all_sources_have_nearby_receptors': all(len(n)>0 for n in near), 'replay_48_consecutive_actual_hours': len(replay_idx)==48 and bool(np.all(np.diff(replay_idx)==1))}
    diagnostics = {'sources': len(sites), 'capture_candidates': int(eligible.sum()), 'buffer_sources': int((~eligible).sum()), 'cells': len(cells), 'sparse_links': len(si), 'cells_with_nonzero_annual_index': int((baseline>0).sum()), 'allocated_population_all_retained_tracts': float(pop[0].sum()), 'population_in_cells_with_nonzero_annual_index': float(pop[0,baseline>0].sum()), 'population_count_caveat': 'Coverage statistic only; not an affected-residents estimate.', 'population_conservation_max_abs_error': max(errors), 'weather_assignment_distance_km_max': float(weather_distance.max()), 'calm_location_hours_fraction': float((speeds<0.5).mean()), 'annual_population_weighted_index': total, 'buffer_share_of_annual_index_pct': float(100*benefits[0,~eligible].sum()/total), 'wind_height_sensitivity': {'method': '48 deterministic sampled hours: 00,06,12,18 UTC on first day of every month; comparison only, not annual estimate', 'hours_utc': [times[i]+':00Z' for i in sensitivity_idx], 'index_100m': sens_total100, 'index_10m': sens_total10, 'change_pct': 100*(sens_total10/sens_total100-1)}}
    write('diagnostics.json', diagnostics)
    plots(weather, speeds, directions, replay_idx, replay_times, replay_baseline @ pop[0], benefits[0])
    timing = {'trial_48h_seconds': trial_seconds, 'projected_year_seconds': trial_seconds*8760/48, 'annual_loop_seconds': annual_seconds, 'total_seconds': time.perf_counter()-started, 'peak_rss_bytes': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss, 'peak_rss_platform': 'macOS ru_maxrss bytes', 'chunk_hours': 96, 'dense_hours_sites_cells_allocated': False}
    write('validation.json', {'checks': checks, 'all_passed': all(checks.values()), 'timing_memory': timing, 'diagnostics': diagnostics})
    assert all(checks.values()), checks
    print(json.dumps({'complete': True, 'checks': checks, 'timing': timing}), flush=True)


def plots(weather, speeds, directions, replay_idx, replay_times, totals, benefits):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'figure.facecolor':'#f7f7f4','axes.facecolor':'#f7f7f4','font.size':10})
    bins=np.linspace(0,360,17); counts,_=np.histogram(directions[speeds>=0.5],bins)
    fig,ax=plt.subplots(figsize=(6,6),subplot_kw={'projection':'polar'})
    ax.bar(np.deg2rad((bins[:-1]+bins[1:])/2),counts/counts.sum()*100,width=np.deg2rad(20),color='#178b89')
    ax.set_theta_zero_location('N'); ax.set_theta_direction(-1); ax.set_title('2023 ERA5 100 m wind direction FROM\n9 locations × 8,760 hours; calm hours excluded',pad=26)
    ax.set_ylabel('Share of non-calm location-hours (%)',labelpad=30)
    fig.savefig(OUT/'wind-rose.png',dpi=180,bbox_inches='tight'); plt.close(fig)
    fig,axes=plt.subplots(3,1,figsize=(10,7),sharex=True)
    for j,w in enumerate(weather):
        axes[0].plot(range(48),speeds[j,replay_idx],alpha=.65)
        axes[1].plot(range(48),directions[j,replay_idx],'.',alpha=.5)
    axes[0].set_ylabel('100 m speed (m/s)'); axes[1].set_ylabel('Direction FROM (°)')
    axes[2].plot(range(48),totals/1e6,color='#178b89'); axes[2].set_ylabel('Weighted index\n(millions)'); axes[2].set_xlabel('Hours from '+replay_times[0])
    axes[0].set_title('Actual 48-hour replay • nine ERA5 locations; modeled baseline index')
    fig.tight_layout(); fig.savefig(OUT/'replay-weather-index.png',dpi=180); plt.close(fig)
    fig,ax=plt.subplots(figsize=(9,4.8)); ordered=np.sort(benefits)[::-1]
    ax.plot(np.arange(1,len(ordered)+1),np.cumsum(ordered)/ordered.sum()*100,color='#178b89',lw=2)
    ax.set(xlabel='Sources ranked by annual weighted contribution',ylabel='Cumulative share of modeled index (%)',title='Annual exposure contribution distribution • all 422 sources')
    ax.grid(alpha=.2); fig.tight_layout(); fig.savefig(OUT/'site-contribution-distribution.png',dpi=180); plt.close(fig)

if __name__ == '__main__':
    main()
