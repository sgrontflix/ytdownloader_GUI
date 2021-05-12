import os
import re
import subprocess


def youtube_url_validation(url):
    """
    Checks whether the given URL is a valid YouTube URL or not

    :param url: URL to be validated
    :return: true if the URL given is a valid YouTube URL, false if it is not
    """
    youtube_regex = r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)' \
                    r'\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'

    youtube_regex_match = re.match(youtube_regex, url)

    return youtube_regex_match


def sanitize_string(string):
    """
    Replaces all forbidden characters with '' and removes unnecessary whitespaces
    If the string is empty, the returned string will be 'Title'

    :param string: string to be sanitized
    :return: sanitized string
    """
    chars = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']
    string = string.translate({ord(x): '' for x in chars})

    string = string.strip()

    if not string:
        return 'Title'
    else:
        return string


def remove_files(files):
    """
    Removes all files inside the list passed as argument

    :param files: list containing files to remove
    :return: list of files that couldn't be deleted
    """
    for file in list(files):
        try:
            os.remove(file)
            files.remove(file)
        except OSError:
            pass

    return files


def is_gpu_available():
    try:
        subprocess.check_output('nvidia-smi', shell=True)
        return True
    except Exception:
        return False


def print_status(string): print('[*] ' + string)


def print_error(string): print('[-] ' + string)


def print_good(string): print('[+] ' + string)
