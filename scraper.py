import requests
from bs4 import BeautifulSoup
import csv
import os
import time
from termcolor import colored
import argparse

msg = "Check WordPress versions and plugins for given domains."

parser = argparse.ArgumentParser(description=msg)
parser.add_argument("-o", "--output", help="Save output to a file.")
parser.add_argument("-f", "--file", help="Input file with one domain per line.")
parser.add_argument("-d", "--domain", help="Single domain to check.")
args = parser.parse_args()

# Check if no arguments were provided and print help message
if not any(vars(args).values()):
    parser.print_help()
    exit()

def title():
    title = """                                                   
                                                   
__      ___ __  ___  ___ _ __ __ _ _ __   ___ _ __ 
\ \ /\ / / '_ \/ __|/ __| '__/ _` | '_ \ / _ \ '__|
 \ V  V /| |_) \__ \ (__| | | (_| | |_) |  __/ |   
  \_/\_/ | .__/|___/\___|_|  \__,_| .__/ \___|_|   
         | |                      | |              
         |_|                      |_|              """
    print(colored(title, 'cyan'))
    print(colored('Made by Dovydas', 'magenta'))

prefix = f"{colored('[', 'light_grey', attrs=['bold'])}{colored('+', 'light_blue')}{colored(']', 'light_grey', attrs=['bold'])}"
prefix_err = f"{colored('[', 'light_grey', attrs=['bold'])}{colored('!', 'light_red')}{colored(']', 'light_grey', attrs=['bold'])}"

plugins_file = 'plugins.txt'

def parse_version_range(version_range):
    versions = version_range.split('-')
    if len(versions) == 2:
        return versions[0].strip(), versions[1].strip()
    else:
        return versions[0].strip(), versions[0].strip()

def is_version_in_range(version, min_version, max_version):
    if version == 'Unknown':
        return False

    version_parts = list(map(int, version.split('.')))
    min_parts = list(map(int, min_version.split('.')))
    max_parts = list(map(int, max_version.split('.')))

    # Pad shorter version arrays with zeros for comparison
    while len(version_parts) < len(min_parts):
        version_parts.append(0)
    while len(version_parts) < len(max_parts):
        version_parts.append(0)

    return min_parts <= version_parts <= max_parts

def load_plugin_criteria(file_path):
    plugins = {}
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            plugin_name, version_range = line.split(';')
            plugins[plugin_name.strip()] = parse_version_range(version_range.strip())
    return plugins

def get_wordpress_version_and_plugins(url, plugin_criteria):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://google.com'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find WordPress version
        meta_generator = soup.find('meta', attrs={'name': 'generator'})
        wp_version = None
        if meta_generator and 'WordPress' in meta_generator.get('content', ''):
            wp_version = meta_generator['content'].split()[-1]

        # Find plugins and their versions
        detected_plugins = {}
        for plugin_name, (min_version, max_version) in plugin_criteria.items():
            plugin_url = f'{url}/wp-content/plugins/{plugin_name}/'
            try:
                plugin_response = requests.get(plugin_url, headers=headers, timeout=5)
                if plugin_response.status_code == 200:
                    plugin_version_url = f'{plugin_url}readme.txt'
                    version_response = requests.get(plugin_version_url, headers=headers, timeout=5)
                    if version_response.status_code == 200:
                        version_content = version_response.text
                        version_line = next((line for line in version_content.splitlines() if 'Stable tag:' in line), None)
                        plugin_version = version_line.split(':')[1].strip() if version_line else 'Unknown'
                        if is_version_in_range(plugin_version, min_version, max_version):
                            detected_plugins[plugin_name] = plugin_version
            except requests.RequestException:
                continue
        
        return wp_version, detected_plugins

    except requests.HTTPError:
        print(f"{prefix_err} HTTP error accessing {url}")
    except requests.RequestException:
        print(f"{prefix_err} Request error accessing {url}")
    except Exception as e:
        print(f"{prefix_err} Unexpected error for {url}: {e}")
    
    return None, {}

def process_domain(url, writer, plugin_criteria):
    url = 'https://' + url
    print(f"{prefix} Checking {url}")
    wp_version, plugins = get_wordpress_version_and_plugins(url, plugin_criteria)
    if plugins:
        plugins_str = '; '.join([f"{plugin}={version}" for plugin, version in plugins.items()])
        if writer:
            writer.writerow([url, wp_version, plugins_str])
        if wp_version != None:
            print(f"{prefix} WordPress version for {url}: {wp_version}")
        else:
            print(f"{prefix_err} Couldn't find the wordpress version.")
        print(f"{prefix} Plugins for {url}: {plugins_str}")

def main():
    plugin_criteria = load_plugin_criteria(plugins_file)
    writer = None

    if args.output:
        outfile = open(args.output, 'a', newline='')
        writer = csv.writer(outfile)
        if os.stat(args.output).st_size == 0:
            writer.writerow(['url', 'wordpress_version', 'plugins'])

    if args.domain:
        process_domain(args.domain, writer, plugin_criteria)
    elif args.file:
        with open(args.file, 'r') as infile:
            for line in infile:
                url = line.strip()
                if url:
                    process_domain(url, writer, plugin_criteria)
                time.sleep(1)

    if writer:
        outfile.close()

if __name__ == '__main__':
    title()
    main()
