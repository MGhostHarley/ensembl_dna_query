import argparse
import csv
import datetime
import json
import os.path

import requests

from typing import List
from pprint import pprint as pp


"""
AFTERNOON
1. take terminal input XX
2. refactor code XX
3. better error handling XX
4. Out put errors to file XX
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


################# HELPER FUNCTIONS #################
def is_valid_file(arg: str) -> bool:
    if not os.path.isfile(arg) and not arg.endswith(".txt"):
        return False
    return True


def parse_ensemble_response(response_list: List[List[dict]]) -> List[dict]:
    reduced_list = []
    flattened = [response for responses in response_list for response in responses]

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
    return reduced_list


######################## IO #######################
def open_file(file_name: str) -> List[str]:
    with open(file_name) as file:
        variants = [line.rstrip("\n") for line in file]

    if not variants:
        raise Exception("File is empty")
    return variants


def generate_file_id() -> str:
    timestamp = str(datetime.datetime.now().timestamp())
    return timestamp[: timestamp.index(".")]


def output_results(results: List[List[dict]]) -> None:
    result, errors = results
    file_id = generate_file_id()

    output_file_name = "output_" + file_id + ".tsv"
    error_file_name = "error_" + file_id + ".tsv"

    with open(output_file_name, "w") as output_file:
        dw = csv.DictWriter(output_file, sorted(result[0].keys()), delimiter="\t")
        dw.writeheader()
        dw.writerows(result)

    with open(error_file_name, "w") as error_file:
        dw = csv.DictWriter(error_file, sorted(errors[0].keys()), delimiter="\t")
        dw.writeheader()
        dw.writerows(errors)


def command_parser() -> str:
    parser = argparse.ArgumentParser(
        description="Get variant files",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "file_path",
        help="File path of variant file. Must be .txt and absolute file_path",
        type=str,
    )

    args = parser.parse_args()
    config = vars(args)

    if not is_valid_file(config.get("file_path", None)):
        parser.error(
            f"""The file { config.get('file_path', None)}
            
            1. Does not exist
            2. Is not a .txt file
            
            Please use absolute file_path and .txt file.
            """
        )

    return config.get("file_path", "")


######################## API CALLS #######################
def query_ensemble_api(variants: List[str]) -> List[dict]:
    response_list = []
    error_list = []

    if not variants:
        error_list.append(
            {
                "error_description": "No variants were given.",
            }
        )
        return response_list, error_list

    headers = {"Content-Type": "application/json"}
    base_url = r"http://rest.ensembl.org/vep/human/hgvs/"

    for variant in variants:
        url = base_url + variant
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
            error_list.append(
                {"variant": variant, "connection_error": connection_error}
            )
            print("Error Connecting:", connection_error)
            continue

        except requests.exceptions.Timeout as timeout_error:
            error_list.append({"variant": variant, "timeout_error": timeout_error})
            print("Timeout Error:", timeout_error)
            continue

        except requests.exceptions.RequestException as request_error:
            error_list.append({"variant": variant, "request_error": request_error})
            print("OOps: Something Else", request_error)
            continue

        formatted_response = response.json()
        response_list.append(formatted_response)

    parsed_list = parse_ensemble_response(response_list)
    return parsed_list, error_list


def main() -> None:
    file_path = command_parser()
    print(file_path)

    file_contents = open_file(file_path)
    print(file_contents)

    results = query_ensemble_api(file_contents)
    print(results)
    output_results(results)


main()

# # url = r"http://rest.ensembl.org/vep/human/hgvs/NC_000001.11:g.40819893T>A"
# # # url = r"http://rest.ensembl.org/vep/human/hgvs/NC_000006.12:g.152387156G>A"

# # try:
# #     response = requests.get(url, headers=headers)
# #     response.raise_for_status()
# #     formatted_response = response.json()
# #     pp(formatted_response)


# # except requests.exceptions.HTTPError as errh:
# #     print("Http Error:", errh)
