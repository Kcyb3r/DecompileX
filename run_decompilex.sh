#!/bin/bash
# Unset all proxy environment variables
unset http_proxy https_proxy ftp_proxy all_proxy HTTP_PROXY HTTPS_PROXY FTP_PROXY ALL_PROXY no_proxy NO_PROXY
# Run the script
python3 decompilex.py
