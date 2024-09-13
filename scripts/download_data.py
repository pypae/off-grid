import csv
from pathlib import Path

import requests

data_csv = "../data/ch.swisstopo.swissalti3d-D1J83rm7.csv"
output_dir = "../data/tiles"
here = Path(__file__).parent


def download_file(url, output_path):
    """Download a file from a URL and save it to the given path."""
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        print(f"Downloaded {output_path}")
    else:
        print(f"Failed to download {url}, status code: {response.status_code}")


def main():
    output_dir_path = here / output_dir
    output_dir_path.mkdir(parents=True, exist_ok=True)

    with (here / data_csv).open() as f:
        reader = csv.reader(f)
        for line in reader:
            file_url = line[0]
            file_name = file_url.split("/")[-1]
            output_path = output_dir_path / file_name

            # Download the file
            download_file(file_url, output_path)


if __name__ == "__main__":
    main()
