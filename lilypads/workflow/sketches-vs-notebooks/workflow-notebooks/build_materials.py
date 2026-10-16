"""Rebuild synthetic data and executed reference notebooks (Python 3)."""
from pathlib import Path
import json, io, contextlib, base64, os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
os.chdir(ROOT)
rng = np.random.default_rng(24092026)
(ROOT/'data').mkdir(exist_ok=True)

# All locations, measurements and reference systems are fictional teaching data.
rows=[]
for s in range(1,7):
    for i,d in enumerate(pd.date_range('2022-01-01',periods=24,freq='MS')):
        v=2+s*.4+(3 if s>=4 else 0)+rng.normal(0,.3)
        if i==4: v=55
        unit='ug/L' if i%2 else 'mg/L'
        row=[f'S{s}',str(d.date()),v*(1000 if unit=='ug/L' else 1),unit,0 if i==7 else 1,(s-1)*2]
        rows.append(row)
        if i%6==0:
            duplicate=row.copy(); duplicate[2]*=1.05; rows.append(duplicate)
pd.DataFrame(rows,columns=['station','date','nitrate','unit','qc_complete','distance_km']).to_csv('data/hydrology.csv',index=False)

n=500
x=np.clip(rng.normal(25,12,n),0.1,59.9); y=np.clip(rng.normal(30,13,n),.1,59.9)
q=pd.DataFrame({'event_id':[f'E{i:04}' for i in range(n)],'time':pd.date_range('2013-01-01', '2025-12-31',periods=n),'longitude':-120+x/(111.195*np.cos(np.deg2rad(35))), 'latitude':35+y/111.195,'magnitude':rng.uniform(1,4,n).round(2)})
q.loc[10:15,'latitude']=np.nan
pd.concat([q,q.iloc[30:45]],ignore_index=True).to_csv('data/seismology.csv',index=False)

rows=[]
for p in range(4):
    for j,z in enumerate(np.arange(0,561,5)):
        t=5+18*np.exp(-z/110)+rng.normal(0,.25)
        rows.append([f'P{p+1}',z*100 if p%2 else z,'cm' if p%2 else 'm',t+273.15 if p>=2 else t,'K' if p>=2 else 'C',1 if j%19==0 else (np.nan if j%23==0 else 0)])
pd.DataFrame(rows,columns=['profile','depth','depth_unit','temperature','temperature_unit','QA']).to_csv('data/oceanography.csv',index=False)

rows=[]
for s,(ve,vn) in enumerate([(4,2),(2,5),(-3,1),(1,-2)],1):
    dates=pd.date_range('2019-01-01','2023-12-31' if s<4 else '2020-12-31')
    for i,d in enumerate(dates):
        t=i/365.25; frame='B' if i%2 else 'A'; factor=1000 if i%3==0 else 1
        # B has known constant offsets in this invented local frame.
        east=ve*t+rng.normal(0,.6)+(100 if frame=='B' else 0)
        north=vn*t+rng.normal(0,.6)+(-50 if frame=='B' else 0)
        rows.append([f'G{s}',str(d.date()),east/factor,north/factor,'m' if factor==1000 else 'mm',frame,12 if i%31==0 else 2,0 if i%43==0 else 1,s*10,s*6])
pd.DataFrame(rows,columns=['station','date','east','north','unit','frame','horizontal_uncertainty_mm','qc_complete','map_east_km','map_north_km']).to_csv('data/geophysics.csv',index=False)

def md(text): return {'cell_type':'markdown','metadata':{},'source':text.splitlines(True)}
def code(text): return {'cell_type':'code','metadata':{},'execution_count':None,'outputs':[],'source':text.splitlines(True)}
def step(title,inputs,parameters,output,source,note=''):
    return [md(f'## {title}\n\n**Input:** {inputs}\n\n**Parameters and decisions:** {parameters}\n\n**Output:** {output}\n\n{note}'),code(source)]
def build(name,question,schema,steps,conclusion):
    cells=[md(f'# {name.title()}: from sketch to notebook\n\n**Question:** {question}\n\nReference notebook for The Pond. All observations and locations are **synthetic**, created for this activity; results are not evidence about a real site.\n\nFollow each input → analysis → output connection in your sketch. An output can be a named Python object in memory: it does not need its own file. Markdown explains meaning and choices; code performs the operation; displayed tables and figures let us inspect the result.\n\n## Read the data\n\n'+schema),code(f"import numpy as np\nimport pandas as pd\nimport matplotlib.pyplot as plt\n\nraw = pd.read_csv('data/{name}.csv')\nprint(f'Input: {{len(raw)}} rows')\nprint(raw.head().to_string(index=False))")]
    for s in steps: cells.extend(s)
    cells.append(md('## Interpret and connect back to the sketch\n\n'+conclusion+'\n\nChoose one intermediate output. Which later step uses it? Which parameter could change the final result? Explain what the output contains, including its units and what one row represents.'))
    ns={}; count=0
    for c in cells:
        if c['cell_type']!='code':continue
        count+=1; buf=io.StringIO()
        with contextlib.redirect_stdout(buf):exec(''.join(c['source']),ns)
        c['execution_count']=count
        if buf.getvalue():c['outputs'].append({'output_type':'stream','name':'stdout','text':buf.getvalue().splitlines(True)})
        for num in plt.get_fignums():
            b=io.BytesIO();plt.figure(num).savefig(b,format='png',dpi=110,bbox_inches='tight')
            c['outputs'].append({'output_type':'display_data','metadata':{},'data':{'image/png':base64.b64encode(b.getvalue()).decode()}})
        plt.close('all')
    nb={'nbformat':4,'nbformat_minor':4,'metadata':{'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python','version':__import__('platform').python_version()}},'cells':cells}
    Path(f'{name}.ipynb').write_text(json.dumps(nb,indent=1))
    print(name, 'executed',count,'code cells')

build('hydrology','Does water quality change as a stream flows past a developed area?',
'''One row is one nitrate measurement. `station` and `date` identify a sample; `nitrate` uses the row's `unit` (mg/L or ug/L). `qc_complete`: 1 = completed and accepted, 0 = incomplete. `distance_km` increases downstream. The developed reach lies between 4 and 6 km. Repeated station/date pairs are replicate measurements.''',[
step('1. Standardize units','raw measurements','1 mg/L = 1000 ug/L','standardized: one row per original measurement, nitrate_mg_L in mg/L',"standardized = raw.copy()\nstandardized['nitrate_mg_L'] = standardized['nitrate'] * standardized['unit'].map({'mg/L':1, 'ug/L':.001})\nassert standardized['nitrate_mg_L'].notna().all()\nprint(standardized.head().to_string(index=False))"),
step('2. Average duplicates','standardized','Group by station and date; arithmetic mean. A group passes QC only if every member has qc_complete = 1.','averaged: one row per station/date, with replicate count',"averaged = standardized.groupby(['station','date'],as_index=False).agg(nitrate_mg_L=('nitrate_mg_L','mean'), qc_complete=('qc_complete','min'), distance_km=('distance_km','first'), replicates=('nitrate_mg_L','size'))\nprint(f'{len(standardized)} measurements → {len(averaged)} station/date samples')",'This explicit group-QC rule preserves the sketch’s order: average first, then filter. It is an added teaching choice; the sketch does not specify how duplicate flags combine.'),
step('3. Apply quality control','averaged','Keep qc_complete = 1','quality: accepted station/date samples',"quality = averaged.loc[averaged.qc_complete.eq(1)].copy()\nprint(f'{len(averaged)} → {len(quality)} samples')"),
step('4. Apply measurement range','quality','Maximum nitrate = 50 mg/L, inclusive. Synthetic inputs contain no negative values.','filtered: accepted samples within the measurement range',"MAX_NITRATE_MG_L = 50\nfiltered = quality.loc[quality.nitrate_mg_L.le(MAX_NITRATE_MG_L)].copy()\nassert filtered.nitrate_mg_L.between(0,50).all()\nprint(f'{len(quality)} → {len(filtered)} samples')"),
step('5. Calculate station means','filtered','Arithmetic mean across dates; each retained station/date gets equal weight','station_means: one row per station; mean nitrate in mg/L and sample count',"station_means = filtered.groupby('station',as_index=False).agg(mean_nitrate_mg_L=('nitrate_mg_L','mean'), n_dates=('date','size'), distance_km=('distance_km','first')).sort_values('distance_km')\nprint(station_means.to_string(index=False))"),
step('6. Plot along the stream','station_means','Distance increases downstream; developed reach 4–6 km','A figure relating station mean nitrate to downstream distance',"fig, ax = plt.subplots(figsize=(7,4))\nax.plot(station_means.distance_km,station_means.mean_nitrate_mg_L,'o-')\nax.axvspan(4,6,alpha=.15,color='gray',label='Developed reach')\nax.set(xlabel='Distance downstream (km)',ylabel='Mean nitrate (mg/L)',title='Synthetic stream observations')\nax.legend(); fig.tight_layout()")], 'The synthetic station means increase downstream of the developed reach. This spatial association alone cannot establish its cause.')

build('seismology','Where are earthquakes occurring most frequently in a given region?',
'''One row is a catalog record. `event_id` identifies an earthquake, `time` is UTC, latitude/longitude are degrees, and magnitude is a dimensionless catalog value. Duplicate identifiers here have identical contents. For the exercise, assume completeness at magnitude ≥2 during 2015–2024.''',[
step('1. Remove duplicates','raw catalog','Keep first occurrence of each event_id; duplicates in this dataset are identical','unique: one row per event',"unique = raw.drop_duplicates('event_id').copy()\nunique['time'] = pd.to_datetime(unique['time'],utc=True)\nprint(f'{len(raw)} → {len(unique)} records')"),
step('2. Require locations','unique','Both latitude and longitude must be present','located: events with coordinates',"located = unique.dropna(subset=['latitude','longitude']).copy()\nprint(f'{len(unique)} → {len(located)} events')"),
step('3. Select dates','located','2015-01-01 inclusive to 2025-01-01 exclusive (UTC)','dated: events during 2015–2024',"START = '2015-01-01'\nSTOP = '2025-01-01'\ndated = located.loc[located.time.ge(START) & located.time.lt(STOP)].copy()\nprint(f'{len(located)} → {len(dated)} events')"),
step('4. Select magnitudes','dated','Minimum magnitude = 2.0, inclusive','selected: events meeting the completeness assumption',"MIN_MAGNITUDE = 2.0\nselected = dated.loc[dated.magnitude.ge(MIN_MAGNITUDE)].copy()\nprint(f'{len(dated)} → {len(selected)} events')"),
step('5. Define spatial cells and count','selected','10 km cells; local origin 35°N, 120°W; fixed domain 0–60 km east and north','counts: 6 × 6 array of event counts; x_edges and y_edges: boundaries in km',"CELL_KM = 10\nLAT0, LON0 = 35., -120.\nKM_PER_DEGREE = 111.195\nspatial = selected.copy()\nspatial['east_km'] = (spatial.longitude-LON0)*KM_PER_DEGREE*np.cos(np.deg2rad(LAT0))\nspatial['north_km'] = (spatial.latitude-LAT0)*KM_PER_DEGREE\nassert spatial.east_km.between(0,60).all() and spatial.north_km.between(0,60).all()\nx_edges = y_edges = np.arange(0,60+CELL_KM,CELL_KM)\ncounts, x_edges, y_edges = np.histogram2d(spatial.east_km,spatial.north_km,bins=[x_edges,y_edges])\nassert counts.sum() == len(selected)\nprint('Total events counted:',int(counts.sum()))\nprint('Largest cell count:',int(counts.max()))",'Teaching simplification: use an approximate local equirectangular coordinate system, not equal increments of latitude/longitude. Cells are nominally 10 × 10 km; a real regional analysis should use a suitable projected CRS. Cell intervals include the lower edge and exclude the upper, except the final upper edge. Counts cover the whole period, not events per year.'),
step('6. Map event counts','counts and grid boundaries','Transpose array so east is horizontal; include zero-count cells','Local-coordinate map with number of events per cell',"fig, ax = plt.subplots(figsize=(6,5))\nim = ax.pcolormesh(x_edges,y_edges,counts.T,cmap='viridis',shading='flat')\nfig.colorbar(im,ax=ax,label='Earthquakes per cell (2015–2024)')\nax.set(xlabel='East of origin (km)',ylabel='North of origin (km)',title='Synthetic earthquake counts',aspect='equal')\nfig.tight_layout()")], 'The highest-count cells identify the most frequent recorded activity under these selection and grid choices. This is not a seismic hazard estimate.')

build('oceanography','How does ocean temperature change with depth?',
'''One row is one observation within `profile`. `depth_unit` is m or cm; `temperature_unit` is C or K. `QA`: 0 = valid, 1 = invalid, blank = not checked. Depth is positive downward. Profiles share a fictional location.''',[
step('1. Convert depths','raw','cm to m: divide by 100','depths: original rows with depth_m',"depths = raw.copy()\ndepths['depth_m'] = depths.depth*depths.depth_unit.map({'m':1,'cm':.01})\nprint(depths[['profile','depth','depth_unit','depth_m']].head().to_string(index=False))"),
step('2. Convert temperatures','depths','Kelvin to Celsius: subtract 273.15','standardized: original observations with depth_m and temperature_C',"standardized = depths.copy()\nstandardized['temperature_C'] = standardized.temperature - standardized.temperature_unit.map({'C':0,'K':273.15})\nassert standardized[['depth_m','temperature_C']].notna().all().all()\nprint(standardized[['profile','depth_m','temperature_C']].head().to_string(index=False))"),
step('3. Apply quality control','standardized','Keep QA = 0; discard both invalid and unchecked observations','quality: valid measurements',"quality = standardized.loc[standardized.QA.eq(0)].copy()\nprint(f'{len(standardized)} → {len(quality)} observations')"),
step('4. Select upper ocean','quality','0 ≤ depth ≤ 500 m','upper: valid measurements in the upper 500 m',"MAX_DEPTH_M = 500\nupper = quality.loc[quality.depth_m.between(0,MAX_DEPTH_M)].copy()\nprint(f'{len(quality)} → {len(upper)} observations')"),
step('5. Bin depths and average','upper','10 m intervals; equal weight per measurement across profiles; intervals [0,10), …, [490,500]','binned: observations assigned to bins; profile_mean: one row per interval, mean °C and count',"BIN_M = 10\nbinned = upper.copy()\nbinned['bin_index'] = np.minimum((binned.depth_m//BIN_M).astype(int),MAX_DEPTH_M//BIN_M-1)\nprofile_mean = binned.groupby('bin_index').agg(mean_temperature_C=('temperature_C','mean'), n=('temperature_C','size')).reindex(range(MAX_DEPTH_M//BIN_M))\nprofile_mean['midpoint_m'] = (profile_mean.index+.5)*BIN_M\nprofile_mean['n'] = profile_mean['n'].fillna(0).astype(int)\nassert profile_mean.n.sum() == len(upper)\nprint(profile_mean.head().to_string())",'An empty interval has no mean (NaN); we do not interpolate. This is a pooled measurement mean, not an equal-weight average of profile means.'),
step('6. Plot temperature against depth','profile_mean','Plot at interval midpoints; invert depth axis','Mean temperature profile',"fig, ax = plt.subplots(figsize=(5,6))\nax.plot(profile_mean.mean_temperature_C,profile_mean.midpoint_m,'o-',markersize=3)\nax.invert_yaxis()\nax.set(xlabel='Mean temperature (°C)',ylabel='Depth (m)',title='Synthetic ocean temperature profile')\nfig.tight_layout()")], 'The synthetic ocean cools with depth, with the strongest change near the surface. Bin width determines how much vertical detail the summary retains.')

build('geophysics','Is the ground moving in this area over time?',
'''One row is a daily GNSS-like observation. `east` and `north` are local horizontal positions in the stated `unit` (m or mm). `frame` is fictional A or B. Frame B adds +100 mm east and −50 mm north relative to A. `horizontal_uncertainty_mm` is a supplied scalar horizontal uncertainty, already in mm. `qc_complete`: 1 = completed and accepted, 0 = incomplete. `map_east_km` and `map_north_km` locate stations in a fictional local map.\n\n**Teaching simplification:** constant offsets demonstrate reference-frame bookkeeping. They are not a realistic transformation between terrestrial GNSS reference frames.''',[
step('1. Standardize positions','raw','Target frame A; target unit mm. Convert units before removing B offsets.','standardized: positions in A, in mm, with parsed dates',"standardized = raw.copy()\nstandardized['date'] = pd.to_datetime(standardized.date)\nfactor = standardized.unit.map({'m':1000,'mm':1})\nstandardized['east_mm'] = standardized.east*factor-standardized.frame.map({'A':0,'B':100})\nstandardized['north_mm'] = standardized.north*factor-standardized.frame.map({'A':0,'B':-50})\nassert standardized[['east_mm','north_mm']].notna().all().all()\nprint(standardized[['station','date','east_mm','north_mm']].head().to_string(index=False))"),
step('2. Apply quality control','standardized','Keep qc_complete = 1','quality: accepted daily observations',"quality = standardized.loc[standardized.qc_complete.eq(1)].copy()\nprint(f'{len(standardized)} → {len(quality)} observations')"),
step('3. Filter uncertainty','quality','Horizontal uncertainty ≤10 mm','precise: retained daily observations',"MAX_UNCERTAINTY_MM = 10\nprecise = quality.loc[quality.horizontal_uncertainty_mm.le(MAX_UNCERTAINTY_MM)].copy()\nprint(f'{len(quality)} → {len(precise)} observations')"),
step('4. Select sufficiently long records','precise','At least 3 years between first and last retained observation; 1 year = 365.25 days','record_lengths: station spans; eligible: observations from qualifying stations',"MIN_YEARS = 3\nDAYS_PER_YEAR = 365.25\nrecord_lengths = precise.groupby('station').date.agg(['min','max'])\nrecord_lengths['years'] = (record_lengths['max']-record_lengths['min']).dt.days/DAYS_PER_YEAR\nkeep = record_lengths.index[record_lengths.years.ge(MIN_YEARS)]\neligible = precise.loc[precise.station.isin(keep)].copy()\nprint(record_lengths.to_string())\nassert set(keep) == {'G1','G2','G3'}",'Here record length means elapsed span after filtering, not a count of 1,096 valid days. No additional completeness criterion is imposed; real records with long gaps need further assessment.'),
step('5. Fit horizontal trends','eligible','Separate ordinary least-squares lines with intercepts; time in years from each station’s first retained date; no uncertainty weighting','trends: one row per station, east and north velocities in mm/year',"records = []\nfor station, group in eligible.groupby('station'):\n    t = (group.date-group.date.min()).dt.total_seconds()/(86400*DAYS_PER_YEAR)\n    east_rate, east_intercept = np.polyfit(t,group.east_mm,1)\n    north_rate, north_intercept = np.polyfit(t,group.north_mm,1)\n    records.append({'station':station,'east_mm_yr':east_rate,'north_mm_yr':north_rate,'map_east_km':group.map_east_km.iloc[0],'map_north_km':group.map_north_km.iloc[0]})\ntrends = pd.DataFrame(records)\nprint(trends.to_string(index=False))",'These simple teaching fits omit seasonal terms, offsets and correlated noise. No inferential uncertainty or claim of statistical significance is provided.'),
step('6. Combine components','trends','Speed = square root of summed squared components; direction clockwise from north in [0,360) degrees','velocities: station rates plus speed and direction',"velocities = trends.copy()\nvelocities['speed_mm_yr'] = np.hypot(velocities.east_mm_yr,velocities.north_mm_yr)\nvelocities['direction_deg'] = np.degrees(np.arctan2(velocities.east_mm_yr,velocities.north_mm_yr))%360\nvelocities.loc[velocities.speed_mm_yr.eq(0),'direction_deg'] = np.nan\nprint(velocities.to_string(index=False))"),
step('7. Map velocities','velocities','Arrow components in mm/year; map coordinates in km; labeled reference arrow','Local station map with velocity arrows',"fig, ax = plt.subplots(figsize=(7,5))\nq = ax.quiver(velocities.map_east_km,velocities.map_north_km,velocities.east_mm_yr,velocities.north_mm_yr,angles='xy',scale_units='xy',scale=.6)\nax.quiverkey(q,.8,.95,5,'5 mm/year',coordinates='axes')\nfor row in velocities.itertuples():\n    ax.text(row.map_east_km,row.map_north_km-1,row.station)\nax.set(xlim=(0,45),ylim=(0,35),aspect='equal',xlabel='Local east (km)',ylabel='Local north (km)',title='Synthetic horizontal velocities')\nfig.tight_layout()")], 'The retained stations have different movement directions and speeds in the chosen synthetic frame. G4 is excluded because its retained record spans less than three years.')

Path('requirements.txt').write_text('numpy\npandas\nmatplotlib\njupyterlab\n')
Path('README.md').write_text('''# From workflow sketch to notebook — reference materials

Four Python reference notebooks and matching synthetic CSV datasets for The Pond.
Unzip the complete folder, install requirements with `python -m pip install -r requirements.txt`,
then open JupyterLab from this folder. Keep the data folder next to the notebooks.
Each notebook already contains captured outputs; run all cells from top to bottom to reproduce them.
No network access is needed after installing dependencies. No intermediate dataset is written to disk.

## Contents
- hydrology.ipynb — duplicate averaging, QC, measurement range, station means.
- seismology.ipynb — catalog cleaning, date/magnitude selection, spatial counts.
- oceanography.ipynb — unit conversion, QA, depth selection, binned means.
- geophysics.ipynb — simplified frame conversion, filtering, station trends and velocities.
- data/*.csv — synthetic inputs; field meanings are in each notebook.
- build_materials.py — deterministic generator (seed 24092026), which recreates data and notebooks.

## Suggested learner exercise
Use one scenario. Provide the working code and figures, then blank selected Markdown
input/parameter/output descriptions. Learners fill these in by tracing their sketch,
then explain which later cell consumes one intermediate output. Start with one fully
annotated step. Ask learners to predict the effect of changing a parameter before rerunning.
Their edited notebook is their individual response. These delivered notebooks are complete
reference versions, not the blank learner versions.

## Decisions to review before teaching
Hydrology: all duplicate members must pass QC for their mean to pass; dates have equal weight.
Seismology: an approximate local projection is used, with fixed grid origin and extent.
Oceanography: keep QA=0 only, including exclusion of unchecked rows; pool measurements across profiles.
Geophysics: fictional frame offsets, elapsed-span record length, unweighted linear fits.
These choices fill gaps in the sketches and should be made explicit to learners.
All data are fictional; plots illustrate methods, not empirical scientific claims.
''')
