"""GET the all data for all objects from an ENCODE server."""
import requests
import pickle
import json
import os
ALLOBJ = '''user
Donor
award
lab
organism
source
target
publication
document
antibody_lot
antibody_characterization
antibody_approval
treatment
construct
construct_characterization
rnai
rnai_characterization
talen
mouse_donor
fly_donor
worm_donor
human_donor
donor_characterization
biosample
biosample_characterization
platform
library
experiment
replicate
annotation
project
publication_data
reference
ucsc_browser_composite
matched_set
treatment_time_series
treatment_concentration_series
organism_development_series
replication_timing_series
reference_epigenome
software
software_version
analysis_step
analysis_step_version
pipeline
analysis_step_run
file
star_quality_metric
bismark_quality_metric
cpg_correlation_quality_metric
chipseq_filter_quality_metric
encode2_chipseq_quality_metric
fastqc_quality_metric
samtools_flagstats_quality_metric
mad_quality_metric
bigwigcorrelate_quality_metric
dnase_peak_quality_metric
edwbamstats_quality_metric
edwcomparepeaks_quality_metric
hotspot_quality_metric
idr_summary_quality_metric
pbc_quality_metric
phantompeaktools_spp_quality_metric
samtools_stats_quality_metric
idr_quality_metric
generic_quality_metric
image
page
user
publication
biosample
library
experiment
annotation
project
publication_data
reference
ucsc_browser_composite
matched_set
treatment_time_series
treatment_concentration_series
organism_development_series
replication_timing_series
reference_epigenome'''

OBJlist = ALLOBJ.split('\n')


for OBJ in OBJlist:
    Obj = OBJ
    Opt = "&frame=object&limit=all&format=json"

    Fname = "EncodeMetaAll/All_{}.p".format(Obj)
    if os.path.isfile(Fname):
        #print '{} \t is already stored, it is skipped'.format(Obj)
        continue
    #print '{} \t is processing'.format(Obj)

    # Force return from the server in JSON format
    HEADERS = {'accept': 'application/json'}

    # This searches the ENCODE database for the phrase "bone chip"
    URL = "https://www.encodeproject.org/search/?type={}{}".format(Obj, Opt)
    # print URL

    # GET the search result
    response = requests.get(URL, headers=HEADERS)

    # Extract the JSON response as a python dict
    response_json_dict = response.json()

    # Write dictionary to pickle
    pickle.dump(response_json_dict, open(Fname, "wb"))
    filesize = os.path.getsize(Fname)
    print OBJ, len(response_json_dict)
    '''
        print response_json_dict
        # print "\"{}\" may not be the correct object name, please check again"\
        #     .format(Obj)
        os.remove(Fname)
        break
    '''


# Print the object
# print json.dumps(response_json_dict, indent=4, separators=(',', ': '))
