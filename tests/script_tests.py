# -*- coding: utf-8 -*-
"""
    tests.script_tests
    ~~~~~~~~~~~~~~~~~~

    Tests for the Eww client.

"""

from nose.tools import assert_raises

import eww
from scripts import eww as client
from utils import *

def test_eww_client():
    """Tests some basic eww client functionality."""

    eww_client = client.EwwClient(host='localhost', port=10000)

    assert eww_client.host == 'localhost'
    assert eww_client.port == 10000
    assert '(eww) ' in eww_client.prompts
    assert '>>> ' in eww_client.prompts
    assert '... ' in eww_client.prompts

def test_connect():
    """Just want to make sure nothing raises here."""

    eww.embed(timeout=0.01)
    assert expected_thread_count(3)

    eww_client = connect_via_client()
    eww_client.sock.close()

    eww.remove()

def test_display_output():
    """Tests client.EwwClient.display_output"""

    eww.embed(timeout=0.01)
    assert expected_thread_count(3)

    eww_client = connect_via_client()

    with CaptureOutput(proxy=True) as output:
        eww_client.display_output()
    output = output.stdout.getvalue()

    assert 'Eww' in output
    assert 'help' in output
    assert 'PID' in output
    assert 'Name' in output

    assert eww_client.current_prompt == '(eww) '

    eww.remove()

    eww_client.sock.close()

    raises = False
    try:
        eww_client.display_output()
    except client.ConnectionClosed:
        raises = True
    assert raises

    eww.embed(timeout=0.01)
    assert expected_thread_count(3)

    eww_client = connect_via_client()

    with CaptureOutput(proxy=True):
        eww_client.display_output()

    eww.remove()

    raises = False
    try:
        eww_client.display_output()
    except client.ConnectionClosed:
        raises = True
    assert raises

def test_get_input():
    """Tests client.EwwClient.get_input"""
    eww.embed(timeout=0.01)
    assert expected_thread_count(3)

    eww_client = connect_via_client()

    with CaptureOutput(proxy=True):
        eww_client.display_output()

    eww_client.get_input(line='Gahakafaka')

    with CaptureOutput(proxy=True) as output:
        eww_client.display_output()
    output = output.stdout.getvalue()

    assert output == 'Command unrecognized.\n'

    eww_client.sock.close()

    eww_client = connect_via_client()
    with CaptureOutput(proxy=True):
        eww_client.display_output()

    eww_client.sock.shutdown(socket.SHUT_RDWR)

    raises = False
    try:
        eww_client.get_input(line='exit')
    except client.ConnectionClosed:
        raises = True
    assert raises

    eww.remove()

def test_clientloop():
    """Tests client.EwwClient.clientloop().  We test each part on it's own, so
    This is just a sanity check to make sure we don't raise.
    """

    eww.embed(timeout=0.01)
    assert expected_thread_count(3)

    eww_client = connect_via_client()

    with CaptureOutput(proxy=True) as output:
        eww_client.clientloop(debug=True, line='exit')
    output = output.stdout.getvalue()

    assert 'Eww' in output
    assert 'help' in output
    assert 'PID' in output
    assert 'Name' in output

    eww.remove()

def test_main():
    """Tests client.EwwClient.main() as best we can."""

    eww.embed(timeout=0.01)

    with CaptureOutput(proxy=True) as output:
        client.main(debug=True, line='exit', opt_args=[])
    output = output.stdout.getvalue()

    assert 'Eww' in output
    assert 'help' in output
    assert 'PID' in output
    assert 'Name' in output

    eww.remove()

    with CaptureOutput() as output:
        try:
            client.main(debug=True, line='exit', opt_args=[])
        except SystemExit:
            pass
    output = output.stdout.getvalue()

    assert output == 'Connection refused.\n'



































