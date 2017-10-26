# These are parameters that stay the same from query to query (unlike the
# doi):
static_parameters_for_api = {}

user_agent_custom_string = (
        'This is part of a bulk download for a research '
        'project by Jane Doe of the University of ________. '
        'I have put a threshold on the download in order '
        'not to cause a problem with your servers. If this '
        'download IS causing a problem, please feel free to email me at '
        '________, or to call me directly at ________.')

api_base_url = (
            'https://example.com/openurl')

# This dataset is currently expected to contain two columns:
# 'doi' and 'oadoi_color' (containing values 'closed', 'bronze', 'hybrid',
# etc.)
# This may be a local file or a URL. It may also be compressed (e.g., a
# tsv.xz file)
input_tsv_dataset_location = (
        'https://github.com/greenelab/scihub/raw/'
        '4172526ac7433357b31790578ad6f59948b6db26/data/'
        'state-of-oa-dois.tsv.xz')

rerun_dois_that_are_already_in_database = False
