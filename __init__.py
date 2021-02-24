from albert import *
import subprocess
import json
import os
import base64
import binascii
from shutil import which

__title__ = 'Bitwarden'
__version__ = '0.4.1'
__triggers__ = ['bw ', 'bwlogin', 'bwtoken ']
__authors__ = 'tony'


def initialize():
    global icon, session_file
    icon = os.path.dirname(__file__) + '/bitwarden.svg'
    session_file = configLocation() + '/bitwarden_session.txt'


def needToLogin():
    return Item(
        id=__title__,
        icon=icon,
        text='Bitwarden session file was not found!',
        subtext='Log in via \'bwlogin\' Alber command.',
        completion='bwlogin'
    )


def handleQuery(query):
    if not query.isTriggered:
        return None

    if not which('bw'):
        return Item(
            id=__title__,
            icon=icon,
            text='Bitwarden CLI couldn\'t be found.',
            subtext='Refer to Bitwarden\'s documentation to install it. Click enter to open website.',
            actions=[
                UrlAction(text='Open documentation in browser.', url='https://bitwarden.com/help/article/cli/#download-and-install')
            ]
        )

    if query.trigger == 'bwlogin':
        return Item(
            id=__title__,
            icon=icon,
            text='Login to Bitwarden',
            subtext='You will be prompted to enter your Bitwarden details. Your data will be only transfered to Bitwarden server.',
            actions=[
                TermAction(
                    text='Login with token',
                    script='bw logout > /dev/null 2>&1 || true && bw login --raw > ' + session_file
                )
            ]
        )

    if query.trigger == 'bwtoken ':
        if query.string == '':
            return Item(
                id=__title__,
                icon=icon,
                text='Incorrect format',
                subtext='Usage: \'bwtoken (token)\''
            )

        try:
            base64.b64decode(query.string)
        except binascii.Error:
            return Item(
                id=__title__,
                icon=icon,
                text='Incorrect token format',
                subtext='Token should be valid base64 string'
            )

        return Item(
            id=__title__,
            icon=icon,
            text='Login to Bitwarden with token',
            subtext='Token: ' + query.string,
            actions=[
                TermAction(
                    text='Login with token',
                    script='echo \'' + query.string + '\' > ' + session_file
                )
            ]
        )

    try:
        session_token = open(session_file).read().strip()
    except FileNotFoundError:
        return needToLogin()

    if len(query.string.strip()) > 0:
        bw_list = subprocess.run(
            ['bw', 'list', 'items', '--nointeraction', '--search', query.string, '--session', session_token],
            capture_output=True)

        if bw_list.stderr:
            if bw_list.stderr == b'Vault is locked.' or bw_list.stderr == b'You are not logged in.':
                return needToLogin()

            return Item(
                id=__title__,
                icon=icon,
                text='Error: ' + bw_list.stderr,
            )

        results = []

        items = json.loads(bw_list.stdout)

        if not items:
            return Item(
                id=__title__,
                icon=icon,
                text='Nothing found',
                subtext='Bitwarden returned no results for \'' + query.string + '\'.'
            )

        for password in items:
            actions = [
                ClipAction(text='Copy password to clipboard', clipboardText=password['login']['password']),
                ClipAction(text='Copy username to clipboard', clipboardText=password['login']['username']),
            ]

            if password['login']['totp']:
                actions.append(
                    # This should probably be ProcAction but I can't figure out how to copy to clipboard using it
                    # Alternative is to use ClipAction and load OTP codes prior to showing them,
                    # but that creates roughly half second delay for every item which is inconvinient
                    TermAction(
                        text='Copy TOTP to clipboard',
                        script='bw get totp ' + password['id'] + ' --nointeraction --session ' + session_token + ' | xclip -se c',
                    )
                )

            results.append(
                Item(
                    id=__title__,
                    icon=icon,
                    text=password['name'],
                    subtext=password['login']['username']+', click enter to copy password.',
                    completion='bw ' + password['name'],
                    actions=actions
                )
            )

        return results
    else:
        return Item(
            id=__title__,
            icon=icon,
            text='Incorrect format',
            subtext='Usage: \'bw (query)\''
        )
