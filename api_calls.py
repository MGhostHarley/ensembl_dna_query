import argparse
import csv
import json
import os.path

import requests
from pprint import pprint as pp


"""
AFTERNOON
1. take terminal input XX
2. refactor code
3. better error handling
4. Out put errors to file
5. generate timestamp for file names

NIGHT:
1. pytest for testing
2. create a package
3. test.

MONDAY
1. Code walk through
2. Read Me
3. Final Tests

"""

# PARSER


def is_valid_file(arg: str) -> bool:
    if not os.path.isfile(arg) and not arg.endswith(".txt"):
        return False

    return True


parser = argparse.ArgumentParser(
    description="Get variant files",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)
parser.add_argument(
    "file_path", help="File path of variant file. Must be .txt", type=str
)


args = parser.parse_args()
config = vars(args)
file_name = config.get("file_path")

if not is_valid_file(config.get("file_path", None)):
    parser.error(
        f"The file { config.get('file_path', None)} does not exist or is not a .txt file"
    )

print(config)

# READ FILES
with open(file_name) as file:
    variants = [line.rstrip("\n") for line in file]
# print(variants)

# API CALLS HERE


request_list = []
error_list = []
headers = {"Content-Type": "application/json"}
# # url = r"http://rest.ensembl.org/vep/human/hgvs/NC_000001.11:g.40819893T>A"
# # # url = r"http://rest.ensembl.org/vep/human/hgvs/NC_000006.12:g.152387156G>A"

# # try:
# #     response = requests.get(url, headers=headers)
# #     response.raise_for_status()
# #     formatted_response = response.json()
# #     pp(formatted_response)


# # except requests.exceptions.HTTPError as errh:
# #     print("Http Error:", errh)


for variant in variants:
    url = r"http://rest.ensembl.org/vep/human/hgvs/" + variant
    print(url)
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

    except requests.exceptions.HTTPError as http_error:
        error_list.append(
            {
                "variant": variant,
                "http_error": http_error,
                "error_description": response.json(),
            }
        )
        print("Http Error:", http_error)
        continue

    except requests.exceptions.ConnectionError as connection_error:
        error_list.append({"variant": variant, "error": connection_error})
        print("Error Connecting:", connection_error)

    except requests.exceptions.Timeout as timeout_error:
        error_list.append({"variant": variant, "error": timeout_error})
        print("Timeout Error:", timeout_error)

    except requests.exceptions.RequestException as request_error:
        error_list.append({"variant": variant, "error": request_error})
        print("OOps: Something Else", request_error)

    formatted_response = response.json()
    request_list.append(formatted_response)


pp(request_list)
pp(error_list)
print(len(request_list))

"""
    input
    assembly_name
    seq_region_name
    start
    end
    strand
    most_severe_consequence
    transcript_consequences > list > gene_symbol
"""


### PARSING
flattened = [request for requests in request_list for request in requests]
pp(flattened)

reduced_list = []

for flat in flattened:
    reduced_list.append(
        {
            "input": flat.get("input", None),
            "assembly_name": flat.get("assembly_name", None),
            "seq_region_name": flat.get("seq_region_name", None),
            "start": flat.get("start", None),
            "end": flat.get("end", None),
            "strand": flat.get("strand", None),
            "most_severe_consequence": flat.get("most_severe_consequence", None),
            "gene": flat.get("transcript_consequences", None)[0].get(
                "gene_symbol", None
            ),
        }
    )
pp(reduced_list)

### OUTPUT FILES
with open("output.tsv", "w") as output_file:
    dw = csv.DictWriter(output_file, sorted(reduced_list[0].keys()), delimiter="\t")
    dw.writeheader()
    dw.writerows(reduced_list)
