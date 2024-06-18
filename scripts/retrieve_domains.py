import csv
import subprocess


# data source => https://toplists.net.in.tum.de/archive/openpagerank/
def extract_gr_domains(file_path, batch_size=10000, max_domains=1000):
    """
    Extract Greek domain names from an input file.
    :param file_path: the path to the file with domains
    :param batch_size: the batch size with which to process domains
    :param max_domains: maximum amount of domains to extract
    :return: the extracted domains
    """
    extracted_domains = []
    start_line = 1  # starting line number for each batch

    # continue extracting until we have 1000 .gr domains
    while len(extracted_domains) < max_domains:
        # define the end line for the cut command (per batch)
        end_line = start_line + batch_size - 1

        # Use sed and cut to select the domain column (in this case it's the 2nd column) TODO maybe parametrise col number
        # and grep to filter domains that end with .gr (Greek domain in this case)
        command = f"sed -n '{start_line},{end_line}p' {file_path} | cut -d ',' -f2 | " + "grep '\.gr\"$'"
        try:
            result = subprocess.run(command, shell=True, text=True, capture_output=True)

            # collect the domains
            domains = result.stdout.split()
            extracted_domains.extend(domains)
            print(len(extracted_domains))  # see progress
            print("batch" + str(start_line) + "," + str(end_line))
            # if we have more than 1000 domains, stop early TODO maybe truncate the list
            if len(extracted_domains) > max_domains:
                break

            # update the starting line (= prev_val + batch size) for the next batch
            start_line += batch_size
        except Exception as e:
            print(f"An error occurred: {e}")
            break

    return extracted_domains


def remove_quotes(string):
    """
    Remove quotes from a string.
    :param string: the input string
    :return: the string without quotes
    """
    return string.strip('"')
