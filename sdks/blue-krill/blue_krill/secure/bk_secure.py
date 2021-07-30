# -*- coding: utf-8 -*-
"""
 * TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-蓝鲸 PaaS 平台(BlueKing-PaaS) available.
 * Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
 * Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at http://opensource.org/licenses/MIT
 * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
 * an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
 * specific language governing permissions and limitations under the License.
"""

import base64
import sys

import click
import editor
from cryptography.fernet import InvalidToken

from blue_krill.encoding import force_bytes, force_text
from blue_krill.encrypt.utils import decrypt_string, encrypt_string

"""The command line tool for blue_krill.secure module, it's can do follow things:

- encrypt a plain text
- decrypt a encrypted token
- edit a encrypted fernet token and output the new result
"""
COMMAND_HELP = '''The command-line tool for blue_krill.secure module, supported env vars:

- BK_FERNET_KEY: the default fernet key for encryption/decryption, if not set, will prompt for user input
- EDITOR: the default editor for `bk-secure edit` command, recommended value: "vi", "vim"
'''


def validate_key(ctx, param, value) -> bytes:
    """Validate fernet key"""
    b_value = force_bytes(value)

    help_text = '"key" should be a base64 encoded 32-bit string'
    try:
        decoded_value = base64.b64decode(b_value)
    except Exception:
        raise click.BadParameter(help_text)
    if not len(decoded_value) == 32:
        raise click.BadParameter(help_text)

    return b_value


@click.group(help=COMMAND_HELP)
def main():
    """The main entrance"""
    pass


@main.command(help='Encrypt a string into fernet token')
@click.option('--key', envvar='BK_FERNET_KEY', prompt='Input fernet key', callback=validate_key)
@click.option('--input-string', prompt='Input string')
def encrypt(key, input_string):
    """Encrypt a given content"""
    target = encrypt_string(input_string.strip(), key=key)
    click.echo('The encrypted token is: ', nl=False)
    click.echo(click.style(target, fg='red'))


@main.command(help='Decrypt a fernet token into plaintext')
@click.option('--key', envvar='BK_FERNET_KEY', prompt='Input fernet key', callback=validate_key)
@click.option('--input-token', prompt='Input token')
def decrypt(key, input_token):
    """Decrypt a given fernet token"""
    try:
        target = decrypt_string(input_token.strip(), key=key)
    except InvalidToken:
        click.echo('Error: Token is invalid')
        sys.exit(1)

    click.echo('The decrypted result is: ', nl=False)
    click.echo(click.style(target, fg='blue'))


@main.command(help='Edit a fernet token')
@click.option('--key', envvar='BK_FERNET_KEY', prompt='Input fernet key', callback=validate_key)
@click.option('--input-token', prompt='Input token')
def edit(key, input_token):
    """Edit a given fernet token, will call external editor"""
    try:
        target = decrypt_string(input_token.strip(), key=key)
    except InvalidToken:
        click.echo('Error: Token is invalid')
        sys.exit(1)

    # Call external editor for editting value
    new_value = force_text(editor.edit(contents=target)).strip()
    encrypted_new_value = encrypt_string(new_value, key=key)

    # Display the plain new value
    click.echo('The new value is: ', nl=False)
    click.echo(click.style(new_value, fg='blue'))

    # Display the encrypted new value
    click.echo('The encrypted new value is: ', nl=False)
    click.echo(click.style(encrypted_new_value, fg='red'))


if __name__ == '__main__':
    main()
