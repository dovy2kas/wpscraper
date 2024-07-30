# wpscraper
A script that finds the wordpress website's version and it's plugins.

# About
The script will try to find the plugins listed in the `plugins.txt` file. If you want to add a plugin to search for the syntax is simple:
```
plugin; minimum_version - maximum version
```

# Usage
Install the requirements
```
pip install -r requirements.txt
```

Run the script!
```
usage: scraper.py [-h] [-o OUTPUT] [-f FILE] [-d DOMAIN]

Check WordPress versions and plugins for given domains.

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Save output to a file.
  -f FILE, --file FILE  Input file with one domain per line.
  -d DOMAIN, --domain DOMAIN
                        Single domain to check.
```

