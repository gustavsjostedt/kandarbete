"""
This script can be used to extract protein functions from UniProt if
such information is available.

The user can specify an excel-file to be read (read_file),
the target column header in that file (parameter_column should be 
UniProt IDs), an output path, and the headers to be included in the 
output csv-file.

The data is extracted via UniProts REST API in JSON format using
python requests. Uniprot explicitly states that fecthing data 
programmatically is encouraged.

This script is intended to be used once to output a csv-file containing
necessary infomration for further processing in other scripts
"""

import requests
import pandas as pd
import csv

read_file = "ANNOTATED_Affibody_HCP_LIST.xlsx"
parameter_column = 'UniProt'
output_path = "protein_descriptions_output2.csv"
headers = ["index", "uniprot_id", "type", "activity"]

# open session to reduce connectioning overhead
session = requests.Session()

# accepts string as argument
def fetch_protein(uniprot_id):
    url = f"https://rest.uniprot.org/uniprotkb/{uniprot_id}.json"
    try:
        response = session.get(url)
        response.raise_for_status()

        # if no status error:
        data = response.json()
        
        # find singular recommended name in json data
        name_recommended = (data.get("proteinDescription", {})
                            .get("recommendedName", {}))
        name_prot = (name_recommended.get("fullName", {})
                     .get("value","Unspecified protein"))
        
        # iterate through multiple comments and return the functional 
        # comment using next()
        activity_comment = next(
            (comment for comment in data.get("comments", [])
              if comment.get("commentType") == "FUNCTION"),
            {})
        
        activity = (activity_comment
                    .get("texts", [{}])[0]
                    .get("value", "No molecular activity found."))

        return name_prot, activity
    
    # catching errors
    except requests.exceptions.HTTPError as http_err:
        return f"HTTP Error: {http_err}"
    except requests.exceptions.RequestException as req_err:
        return f"Request Error: {req_err}"
    except KeyError:
        return "Error: Unexpected response structure"


# convert target column in file to interable using pandas

df = pd.read_excel(read_file)
id_lst = df[parameter_column].tolist()

# writing output from function iteratively using 
# standard python csv.writer()

with open(output_path, "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(headers)

    #if portion of list is of interest, splice the list
    for index, uniprot_id in enumerate(id_lst[:15]): 
        name_prot, activity = fetch_protein(uniprot_id)
        writer.writerow([index, uniprot_id, name_prot, activity])


# When all specified IDs have been processed:

print("Results have been saved to 'protein_descriptions_output.csv'")
