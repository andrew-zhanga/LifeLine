#!/usr/bin/env python3
"""Create reproducible figures and supported pitch text from final saved model outputs."""
from pathlib import Path
import csv, json, subprocess
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from matplotlib.patches import FancyBboxPatch
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'demo/public/data'; P=ROOT/'presentation'; F=P/'figures'
def read(p): return json.loads(p.read_text())
def save(fig,name):
    fig.savefig(F/(name+'.svg'),bbox_inches='tight',facecolor=fig.get_facecolor())
    fig.savefig(F/(name+'.png'),dpi=180,bbox_inches='tight',facecolor=fig.get_facecolor())
    plt.close(fig)
def main():
    F.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'figure.facecolor':'#091722','axes.facecolor':'#091722','savefig.facecolor':'#091722','text.color':'#e6f1f4','axes.labelcolor':'#c6d8df','xtick.color':'#adc5cf','ytick.color':'#adc5cf','axes.edgecolor':'#45606b','font.family':'DejaVu Sans','font.size':11,'axes.titleweight':'bold'})
    manifest=read(D/'manifest.json'); scenarios=read(D/'scenarios.json')['scenarios']; baseline=read(D/'baseline.json')
    scenario=next(s for s in scenarios if s['budget_usd']==10e6)
    plans={p['preset']:p for p in scenario['plans'] if p.get('preset')}
    financial,balanced,exposure=[plans[n] for n in ['Financial','Balanced','Exposure']]
    residual=read(D/Path(balanced['residual_url']).relative_to('/data'))
    wind=read(ROOT/'data/verified/processed/weather_2023.json')
    directions=np.concatenate([l['hourly']['wind_direction_100m'] for l in wind['locations']])
    counts,edges=np.histogram(directions,bins=np.linspace(0,360,17))
    fig,ax=plt.subplots(figsize=(7,6),subplot_kw={'projection':'polar'})
    ax.set_theta_zero_location('N');ax.set_theta_direction(-1)
    ax.bar(np.deg2rad((edges[:-1]+edges[1:])/2),counts/counts.sum()*100,width=2*np.pi/16*.9,color='#6cd9b5')
    ax.set_title('Where the wind comes from\n2023 · nine ERA5 locations · 100 m',pad=28)
    ax.set_ylabel('Share of 78,840 location-hours (%)',labelpad=32);save(fig,'wind-rose')
    fig,ax=plt.subplots(figsize=(9,5.2))
    points=sorted([p for p in scenario['plans'] if not p.get('disabled_reason')],key=lambda p:p['npv_usd'])
    ax.plot([p['npv_usd']/1e6 for p in points],[p['exposure_reduction_pct'] for p in points],color='#61818e',lw=1)
    for p in points:
        ax.scatter(p['npv_usd']/1e6,p['exposure_reduction_pct'],s=90 if p.get('preset') else 30,color='#6cd9b5' if p.get('preset')=='Balanced' else '#ffbd76',zorder=3)
        if p.get('preset'): ax.annotate(p['name'],(p['npv_usd']/1e6,p['exposure_reduction_pct']),xytext=(8,8),textcoords='offset points')
    ax.set(xlabel='Seven-year screening NPV (USD million)',ylabel='Annual modeled exposure reduction (%)',title='$10m budget · actual feasible portfolio choices')
    ax.grid(alpha=.12);ax.margins(.2);fig.text(.1,.005,'Sampled integer portfolios; connecting line is visual guidance, not an interpolated investment plan.',fontsize=9);save(fig,'frontier')
    receptors=read(ROOT/'data/verified/processed/population_receptors.geojson')['features']
    coords=np.array([f['geometry']['coordinates'] for f in receptors])
    values=np.array(baseline['annual']);after=np.array(residual['annual'])
    good=values>0; norm=LogNorm(vmin=max(np.quantile(values[good],.05),.001),vmax=values.max())
    fig,axes=plt.subplots(1,2,figsize=(12,5.4),sharex=True,sharey=True)
    for ax,v,title in zip(axes,[values,after],['Baseline','After capture · Balanced']):
        sc=ax.scatter(coords[good,0],coords[good,1],c=np.maximum(v[good],norm.vmin),s=14,marker='s',cmap='magma',norm=norm,linewidths=0)
        ax.set(title=title,xlim=(-100.5,-97.25),ylim=(27.25,29.75),xlabel='Longitude');ax.set_aspect(1/np.cos(np.deg2rad(28.5)));ax.set_xticks([-100,-99,-98])
    axes[0].set_ylabel('Latitude');fig.colorbar(sc,ax=axes,shrink=.7,label='Mean hourly relative index · shared logarithmic scale')
    fig.suptitle('Same sources, weather and scale. Only selected source strength changes.',y=1.02)
    save(fig,'before-after')
    fig,ax=plt.subplots(figsize=(12,4));ax.set_xlim(0,12);ax.set_ylim(0,4);ax.axis('off')
    stages=[('OBSERVED / ESTIMATED','2023 flare inventory\nAnnual gas volumes'),('HISTORICAL WEATHER','ERA5 100 m wind\n8,760 hourly records'),('SCREENING MODEL','Sparse source → cell links\nTract population allocation'),('INVESTMENT DECISION','Capture costs + NPV\nBudgeted integer selection')]
    for i,(label,body) in enumerate(stages):
        x=i*3+.08;ax.add_patch(FancyBboxPatch((x,1.2),2.65,1.8,boxstyle='round,pad=0.1',facecolor='#102c3b',edgecolor='#366176'))
        ax.text(x+.14,2.65,label,fontsize=9,color='#6cd9b5');ax.text(x+.14,2.05,body,fontsize=11,va='center')
        if i<3: ax.annotate('',xy=(x+2.91,2.1),xytext=(x+2.68,2.1),arrowprops={'arrowstyle':'->','color':'#ffbd76'})
    ax.text(6,.45,'Deterministic screening + optimization. No trained model, pollutant concentration, or health-outcome estimate.',ha='center',fontsize=10)
    save(fig,'method')
    fig,ax=plt.subplots(figsize=(10,5));ax.axis('off')
    cards=[('8,783','global flare sites'),('392 + 30','candidates + buffer sources'),('78,840','complete weather location-hours'),('763 / 763','tract population joins'),('7,543','allocated population cells'),('48 hours','actual replay; fixed installations')]
    for i,(num,label) in enumerate(cards):
        x=(i%3)*.34;y=.78-(i//3)*.45
        ax.text(x,y,num,fontsize=29,fontweight='bold',color='#6cd9b5',transform=ax.transAxes);ax.text(x,y-.12,label,fontsize=10,transform=ax.transAxes)
    ax.set_title('Historical data coverage · 2023 scenario',loc='left',pad=25);save(fig,'data-coverage')
    sens=read(ROOT/'data/build/portfolios/sensitivity.json')
    # Preserve raw cases with the figure; accept explicit worker fields, never invent values.
    (P/'sensitivity-source.json').write_text(json.dumps(sens,indent=2)+'\n')
    cases=sens.get('cases',[])
    if cases:
        fig,ax=plt.subplots(figsize=(10,5.2))
        labels=[];benefits=[]
        for c in cases:
            result=next((p for p in c.get('plans',[]) if p.get('preset')=='Balanced' and not p.get('disabled_reason')),c.get('plan',c.get('result',c)))
            if 'exposure_reduction_pct' in result:
                label={'capex-low':'Capex −25%', 'capex-high':'Capex +25%', 'capture-50pct':'Capture 50%', 'capture-90pct':'Capture 90% (base)', 'capture-100pct':'Capture 100%', 'annual-decline-15pct':'Annual gas decline 15%', 'gas-price-low':'Gas price $1.50/MMBtu', 'gas-price-high':'Gas price $4.00/MMBtu'}.get(c.get('name'),c.get('name',c.get('id','case')))
                labels.append(label);benefits.append(result['exposure_reduction_pct'])
        if labels:
            ax.barh(labels,benefits,color='#6cd9b5');ax.invert_yaxis();ax.set(xlabel='Annual modeled exposure reduction (%)',title='$5m sensitivity · recomputed Balanced portfolios');fig.text(.12,-.01,'Declared scenario ranges, not confidence intervals. Decline changes future cashflow; exposure is the historical first-year index.',fontsize=9);save(fig,'sensitivity')
        else: plt.close(fig)
    retained=balanced['npv_usd']/financial['npv_usd']*100
    gain=balanced['exposure_reduction_pct']-financial['exposure_reduction_pct']
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    metrics={'scenario_id':scenario['id'],'financial':financial,'balanced':balanced,'exposure':exposure,'npv_retained_pct':retained,'exposure_gain_percentage_points':gain,'source_commit':commit}
    (P/'metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
    with (P/'claims.csv').open('w') as f:
        w=csv.writer(f);w.writerow(['slide','claim','value','unit','source_result_path','scenario','commit','limitation'])
        for row in [(2,'Global positive-volume inventory',8783,'sites','data/verified/processed/validation_report.json','2023','Published satellite estimates'),(3,'Complete weather hours per location',8760,'hours','data/build/exposure/exposure-manifest.json','2023','Coarse ERA5 reanalysis'),(4,'Financial NPV',financial['npv_usd'],'USD','data/build/portfolios/scenarios.json',scenario['id'],'Screening assumptions; not investment advice'),(5,'Balanced NPV retained',retained,'percent','presentation/metrics.json',scenario['id'],'Relative to Financial reference under same assumptions'),(5,'Balanced exposure reduction',balanced['exposure_reduction_pct'],'percent','data/build/portfolios/scenarios.json',scenario['id'],'Relative index, not health outcome'),(5,'Balanced exposure gain over Financial',gain,'percentage points','presentation/metrics.json',scenario['id'],'Same annual denominator including buffer'),(6,'Data join completeness',763,'of 763 tracts','data/verified/processed/validation_report.json','2019–2023 ACS','Data quality, not predictive accuracy')]:
            slide,claim,value,unit,path,sc,lim=row;w.writerow([slide,claim,value,unit,path,sc,commit,lim])
        for slide,claim,value,unit,path,sc,lim in [(1,'Decision: allocate limited capture budget','Gas value and modeled exposure','product scope','docs/PITCH_BRIEF.md','all','Screening, not engineering certification'),(2,'Capture candidates',392,'sites','data/verified/processed/validation_report.json','South Texas bbox','Study box, not official basin boundary'),(2,'Uncapturable background sources',30,'sites','data/build/exposure/exposure-manifest.json','all','Background retained in denominator'),(3,'Wind rose sample count',78840,'location-hours','data/verified/processed/weather_2023.json','2023','Nine coarse ERA5 locations'),(6,'Sensitivity cases',8,'scenarios','data/build/portfolios/sensitivity.json','budget-5m-benchmark','Declared ranges, not confidence intervals'),(7,'Next step: operator pilot','Engineering inputs and independent observations','proposed future work','presentation/qa.md','future','Not completed or validated by this build')]:
            w.writerow([slide,claim,value,unit,path,sc,commit,lim])
    (P/'pitch.md').write_text(f'''# FlareWise · three-minute narration

**0:00–0:25 — The decision.** Gas flaring wastes a potentially useful resource. For an operator with a limited capture budget, the question is where to invest. The projects with the strongest gas economics may differ from those that reduce the most modeled exposure downwind. FlareWise makes that choice inspectable.

**0:25–0:45 — Enter South Texas.** These are 8,783 real sites in the World Bank's 2023 satellite-derived inventory. We focus on a South Texas study box with 392 capture candidates and 30 background sources. This is a historical scenario, not a live pollution monitor.

**0:45–1:15 — Follow real wind.** Play the 48-hour window. The weather changes, and so does the modeled field. The equipment stays fixed. Selection uses all 8,760 hours of the year. We combine coarse ERA5 winds with a relative transport kernel and population allocated within Census tracts. This is screening, not a concentration or health prediction.

**1:15–1:35 — Inspect the inputs.** Open a source to see estimated annual gas and pipeline-distance-based cost. Open a community to see Census population and age context. We distinguish source observations, published estimates, and assumed project costs, rather than hiding those differences behind one score.

**1:35–2:15 — Make the decision.** At $5 million, Financial and Balanced select the same sites: the objectives align. Switch to $10 million to see a distinct tradeoff. The Financial plan selects {len(financial['selected_ids'])} sites, with a seven-year screening NPV of ${financial['npv_usd']/1e6:.2f} million and {financial['exposure_reduction_pct']:.2f}% annual modeled exposure reduction. Balanced selects {len(balanced['selected_ids'])} sites and retains {retained:.2f}% of that NPV while reaching {balanced['exposure_reduction_pct']:.2f}% reduction: a change of {gain:.2f} percentage points. Before and after use identical weather and a shared scale. Only the chosen sources are reduced, using the stated 90% capture assumption.

**2:15–2:40 — Show the tradeoff.** Every plotted point is an actual budget-feasible portfolio with a matching map. The method is deterministic exposure screening plus integer optimization. We verify population conservation, portfolio budgets, source-removal monotonicity, and agreement with an exhaustive small solver example. These are implementation checks, not predictive accuracy.

**2:40–3:00 — Next step.** The practical next step is an operator pilot: replace screening costs with engineering quotes, confirm pipeline access, and compare transport estimates with independent environmental observations. FlareWise provides an auditable way to decide which projects deserve that deeper investigation.
''')
    (P/'slide-outline.md').write_text('''# Seven-slide storyboard

| Slide | Claim | Asset | Speaker / demo cue |
|---|---|---|---|
| 1 — Where should the budget go? | Gas value and people downwind belong in the same decision. | screenshots/01-global.png | Open globe; ask the investment question. |
| 2 — A real historical study | 392 candidates, 30 background sources; dated sources. | figures/data-coverage.png | Fly into South Texas. |
| 3 — Wind changes; equipment stays | Real 48-hour replay; annual selection. | figures/wind-rose.png; screenshots/03-replay.png | Advance hour, inspect a source/community. |
| 4 — Establish the financial baseline | Actual $10m Financial plan; explain $5m alignment first. | figures/frontier.png | Read the Financial NPV and exposure metrics. |
| 5 — See the alternative | Balanced retains stated NPV and changes exposure by measured amount. | figures/before-after.png | Switch plan, then baseline/after at same hour. Use metrics.json numbers. |
| 6 — Explain and verify | Sparse deterministic screening + integer selection. | figures/method.png; figures/sensitivity.png | State verification versus model validation. |
| 7 — Pilot with better inputs | Engineering and environmental validation are the next step. | screenshots/08-methods.png | State costs/access/resolution limits; invite a pilot. |

Claim-by-claim source ledger: claims.csv. All financial figures are screening outcomes under explicit assumptions. Do not state health effects or trained-model accuracy.
''')
    (P/'qa.md').write_text('''# Judge Q&A

**Does capture equipment move with the wind?** No. We select fixed sites using annual mean population-weighted contribution over 8,760 actual hours. Replay changes weather, not selected installations.

**How current is the data?** The scenario uses 2023 flare volumes and ERA5 winds, plus ACS 2019–2023 five-year population estimates. Pipeline geometry vintage is not established as 2023. Nothing is labeled live.

**Are these measured gas volumes?** They are published VIIRS-derived satellite estimates from the World Bank. Annual activity is spread uniformly across the year for screening; hourly flare operation is not observed.

**Where do costs come from?** Explicit scenario coefficients for equipment, capacity and distance to the nearest downloaded pipeline. These are not engineering quotes. Nearest geometry does not establish capacity, access, rights or a feasible connection.

**Is the population map precise?** Tract population and ages are allocated by intersected area to approximately 5 km cells. Totals are conserved, but individual households are not located. Place and tract populations overlap and are never added together.

**Does this measure avoided illness?** No. The output is a relative wind-driven index weighted by population, not pollutant concentration, personal exposure, AQI or a causal health outcome.

**Did you train an AI model?** No. The core is deterministic sparse transport screening and integer portfolio optimization. There are no training images, masks or independent pollutant measurements in the delivered bundle.

**What does Balanced mean?** It maximizes modeled exposure benefit while retaining at least 95% of the positive Financial NPV reference, at the same budget and price. It is unavailable if that positive reference does not exist. Solver status and gaps are retained.

**How robust is this?** The evidence pack varies declared capex, capture fraction and decline assumptions and recomputes portfolios. These are sensitivity scenarios, not confidence intervals.

**What works without internet?** All analytical assets are local. The map can show local study and tract geography without external basemap tiles. A cold visit still needs the local server; this is not a service-worker-installed offline app.
''')
    print(json.dumps({'npv_retained_pct':retained,'exposure_gain_percentage_points':gain,'figures':len(list(F.glob('*.png')))},indent=2))
if __name__=='__main__': main()
