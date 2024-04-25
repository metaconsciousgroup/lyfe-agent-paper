def extract_recent_content(s):
    marker = "\nThen most recently,\n"
    # Find the position of the marker
    pos = s.find(marker)
    # If marker is found, return the substring after the marker
    if pos != -1:
        return s[pos + len(marker):]
    # If marker isn't found, return an empty string or the original string as needed
    return ""