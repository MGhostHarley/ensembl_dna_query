import argparse
import csv
import datetime
import json
import os.path
import requests
import time


from typing import List


################# HELPER FUNCTIONS #################
def is_valid_file(arg: str) -> bool:
    if not os.path.isfile(arg) and not arg.endswith(".txt"):
        return False
    return True


def generate_file_id() -> str:
    timestamp = str(datetime.datetime.now().timestamp())
    return timestamp[: timestamp.index(".")]


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
    return reduced_list


######################## IO #######################
def open_file(file_name: str) -> List[str]:
    with open(file_name) as file:
        variants = [line.rstrip("\n") for line in file]

    if not variants:
        raise Exception("File is empty")
    return variants


def output_results(results: List[List[dict]]) -> None:
    result, errors = results
    file_id = generate_file_id()

    if not os.path.exists("results"):
        os.makedirs("results")

    # System Agnostic filepath creation
    os.path.join("results", f"output_{file_id}.tsv")
    output_file_name = os.path.join("results", f"output_{file_id}.tsv")
    error_file_name = os.path.join("results", f"error_{file_id}.tsv")

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
    requests_per_second = 15
    request_count = 0
    last_request = 0

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

        # Quick and dirty check to see if we need to be rate limited.
        # TO DO: Make this a stand alone decorator
        if request_count >= requests_per_second:
            delta = time.time() - last_request
            if delta < 1:
                print("Rate Limit Per Second Hit")
                time.sleep(1 - delta)
            last_request = time.time()
            request_count = 0

        try:
            response = requests.get(url, headers=headers)
            request_count += 1
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

    file_contents = open_file(file_path)

    results = query_ensemble_api(file_contents)
    output_results(results)


if __name__ == "__main__":
    main()
