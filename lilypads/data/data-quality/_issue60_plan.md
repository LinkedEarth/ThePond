# Metadata exercise

Imagine that you are a city official charged with determining whether schools in your district meet lead (Pb) exposure standards. Sampling in the district is done by various testing companies, with various instruments each with a given nominal precision. State and city procedures mandate that each measurement by replicated at least once (preferably more). The instruments have known biases that can be corrected for. Lead concentrations can be reported in several units:

| Unit Name | Abbreviation | Equivalent to 400 ppm (EPA Play Area Limit) |
| :--- | :--- | :--- |
| **Parts per million** | ppm | 400 ppm |
| **Milligrams per kilogram** | mg/kg | 400 mg/kg |
| **Micrograms per gram** | µg/g | 400 µg/g |
| **Parts per billion** | ppb | 400,000 ppb |
| **Percent by weight** | % | 0.04% |

The recommended thresholds also vary by medium: 

| Medium | Specific Target Type | EPA Threshold Value |
| :--- | :--- | :--- |
| **Paint / Dust** | Liquid/Surface Paint Limit | 90 ppm (0.009%) |
| **Soil** | Bare Soil Child Play Areas | 400 ppm |
| **Tap Water** | Public Utility Action Level | 10 ppb (0.010 mg/L) |


## Activity 1: Where did this value come from?
 One day, a new employee of yours hands you a spreadsheet that looks like this:

 [cue table of imaginary numbers with columns: sample ID, location,  value, safe?]

Notes: 
- location: use the school name in capital letters, like "FAIRVIEW ELEM." )
- safe?: a boolean (yes/no)

Idea: have learners ask themselves how the safety determination was made. Values given have to be averages, but it doesn't say of how many samples, in what units, and with what precision. 

Next, ask them about the same table coming from a senior employee. Idea: it's a confusor; employee age is not the relevant variable here; metadata quality is. 


A better dataset would look like this:
[cue table of imaginary numbers with columns: sample ID, location, medium, # replicates, instrument, value, units, precision, threshold, safe(?)]  

Notes: 
- location: use the school name in capital letters, like "FAIRVIEW ELEM." )
- medium: see table 2 above
- units: see table 1 above
- threshold: see table 2 above 

Ask learners:

- Which stage of the data has actually been archived?  [the average]
- Can the processed value be traced back to the original observations? [no: those have not been archived, and should be]
- What transformations occurred? [averaging+ comparison ]
- Are those transformations documented? [not explicitly, but they can be inferred with proper metadata. E.g. the reported medium tells us which units and thresholds were likely used, though it would be better to make this explicit]
- Could another researcher reproduce the processed value? [not without the actual workflow --> link to workflow Lilypad page]

How to improve this? 

Give relevant examples of ancillary evidence:
- calibration records
- instrument logs
- field notes
- replicate measurements
- standards/reference materials
- processing code
- photographs or images
- sample metadata

Key idea: Evidence supporting data quality may exist outside the numerical dataset itself.


## Activity 2:   What does this number actually mean?

Look at https://github.com/LinkedEarth/ThePond/issues/60, but instead of temperature, keep using the lead measurement example, with similar considerations of precision, accuracy, and uncertainty (standard error of the mean, assuming independence) 


