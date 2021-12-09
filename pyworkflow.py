
import requests
import pandas as pd


##base_id = DESTINY_BASE_ID
table_name= 'Students'
endpoint1=F'https://api.airtable.com/v0/{base_id}/{table_name}'
##pi_key = AIR_API_KEY

def airtable_download(table, params_dict={}, api_key=None, base_id=None, record_id=None):
  

    # Authorization Credentials
    if api_key is None:
        print("Enter Airtable API key. \n  *Find under Airtable Account Overview: https://airtable.com/account")
        api_key = input()
    headers = {"Authorization": "Bearer {}".format(api_key)}
    validate_airtable_kwargs(api_key, "API key", "key")

    # Locate Base
    if base_id is None:
        print("Enter Airtable Base ID. \n  *Find under Airtable API Documentation: https://airtable.com/api for specific base")
        base_id = input()
    url = 'https://api.airtable.com/v0/{}/'.format(base_id)
    path = url + table
    validate_airtable_kwargs(base_id, "Base ID", "app")

    # Validate Record ID
    if record_id is not None:
        validate_airtable_kwargs(record_id, "Record ID", "rec")

    # Format parameters for request
    constant_params = ()
    for parameter in params_dict:
        constant_params += ((parameter, params_dict[parameter]),)
    params = constant_params

    # Start with blank list of records
    airtable_records = []

    # Retrieve multiple records
    if record_id is None:
        run = True
        while run is True:
            response = requests.get(path, params=params, headers=headers)
            airtable_response = response.json()

            try:
                airtable_records += (airtable_response['records'])
            except:
                if 'error' in airtable_response:
                    identify_errors(airtable_response)
                    return airtable_response

            if 'offset' in airtable_response:
                run = True
                params = (('offset', airtable_response['offset']),) + constant_params
            else:
                run = False

    # Retrieve single record
    if record_id is not None:
        if params_dict != {}:
            print("⚠️ Caution: parameters are redundant for single record lookups. Consider removing `params_dict` argument.")
        path = "{}/{}".format(path, record_id)
        response = requests.get(path, headers=headers)
        airtable_response = response.json()

        if 'error' in airtable_response:
            identify_errors(airtable_response)
            return airtable_response

        airtable_records = [airtable_response]

    return airtable_records


def convert_to_dataframe(airtable_records):
    """Converts dictionary output from airtable_download() into a Pandas dataframe."""
    airtable_rows = []
    airtable_index = []
    for record in airtable_records:
        airtable_rows.append(record['fields'])
        airtable_index.append(record['id'])
    airtable_dataframe = pd.DataFrame(airtable_rows, index=airtable_index)
    return airtable_dataframe


# Troubleshooting Functions
def validate_airtable_kwargs(kwarg, kwarg_name, prefix, char_length=17, print_messages=True):
    """Designed for use with airtable_download() and airtable_upload() functions.
        Checks `api_key`, `base_id` and `record_id` arguments to see if they conform to the expected Airtable API format.
        """
    valid_status = True
    if len(kwarg) != char_length:
        if print_messages is True:
            print("⚠️ Caution: {} not standard length. Make sure API key is {} characters long.".format(kwarg_name, char_length))
        valid_status = False
    if kwarg.startswith(prefix) is False:
        if print_messages is True:
            print("⚠️ Caution: {} doesn't start with `{}`.".format(kwarg_name, prefix))
        valid_status = False
    return valid_status


def identify_errors(airtable_response):
    """Designed for use with airtable_download() and airtable_upload() functions.
        Prints error responses from the Airtable API in an easy-to-read format.
        """
    if 'error' in airtable_response:
        try:
            print('❌ {} error: "{}"'.format(airtable_response['error']['type'], airtable_response['error']['message']))
        except:
            print("❌ Error: {}".format(airtable_response['error']))
    return

##Airtable Download
airtable_records = airtable_download(table_name,params_dict={"view":"meeting_dataframe", "fields" : ["bot_meeting", "eot_meeting", "mot_meeting", "full_name"]},api_key=api_key,base_id=base_id)
#print(airtable_records)

initial_df = convert_to_dataframe(airtable_records)
term_meeting_table = pd.melt(frame=initial_df,
                            id_vars='full_name', 
                            value_vars=['bot_meeting','mot_meeting','eot_meeting'],
                            value_name='status',
                            var_name='meeting'
                           
                            )

