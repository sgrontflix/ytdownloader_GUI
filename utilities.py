import os
import re
import subprocess
from shlex import split
from collections import namedtuple
from functools import reduce


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


"""
The following three functions are needed to avoid using check_output() with shell=True

shell=True should be avoided at all costs as explained here:
https://stackoverflow.com/questions/3172470/actual-meaning-of-shell-true-in-subprocess

Functions are from here:
https://stackoverflow.com/questions/24306205/file-not-found-error-when-launching-a-subprocess-containing-piped-commands
"""
proc_output = namedtuple('proc_output', 'stdout stderr')


def pipeline(starter_command, *commands):
    if not commands:
        try:
            starter_command, *commands = starter_command.split('|')
        except AttributeError:
            pass
    starter_command = _parse(starter_command)
    starter = subprocess.Popen(starter_command, stdout=subprocess.PIPE)
    last_proc = reduce(_create_pipe, map(_parse, commands), starter)
    return proc_output(*last_proc.communicate())


def _create_pipe(previous, command):
    proc = subprocess.Popen(command, stdin=previous.stdout, stdout=subprocess.PIPE)
    previous.stdout.close()
    return proc


def _parse(cmd):
    try:
        return split(cmd)
    except Exception:
        return cmd


def is_gpu_available():
    try:
        pipeline('nvidia-smi')
        return True
    except Exception:
        return False


def print_status(string): print('[*] ' + string)


def print_error(string): print('[-] ' + string)


def print_good(string): print('[+] ' + string)
