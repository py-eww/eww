# -*- coding: utf-8 -*-
"""
    tests.standalone_tests
    ~~~~~~~~~~~~~~~~~~~~~~

    All of the tests in this file can be ran without starting another process.

"""

from collections import deque
from mock import Mock
import os
import socket
import sys
import time
import threading
import __builtin__

from nose.tools import assert_raises

import eww
from eww.shared import DISPATCH_THREAD_NAME, STATS_THREAD_NAME
from eww.stats import InvalidCounterOption, InvalidGraphDatapoint
from utils import *

def test_embed_cycle():
    """Very basic embed/remove test."""
    # Sanity check
    assert expected_thread_count(1)

    eww.embed(timeout=0.01)
    assert expected_thread_count(3)

    eww.remove()
    assert expected_thread_count(1)

def test_proxy_placement():
    """Ensure proxies are setup and torndown correctly."""

    eww.embed(timeout=0.01)

    assert hasattr(sys.stdin, 'register')
    assert hasattr(sys.stdout, 'register')
    assert hasattr(sys.stderr, 'register')
    assert hasattr(__builtin__.quit, 'register')
    assert hasattr(__builtin__.exit, 'register')

    eww.remove()

    assert hasattr(sys.stdin, 'register') == False
    assert hasattr(sys.stdout, 'register') == False
    assert hasattr(sys.stderr, 'register') == False
    assert hasattr(__builtin__.quit, 'register') == False
    assert hasattr(__builtin__.exit, 'register') == False

def test_multiple_calls():
    """Ensure we can call register and unregister in weird ways without
       raising or getting into an inconsistent state."""

    assert expected_thread_count(1)

    eww.remove()
    eww.remove()
    eww.embed(timeout=0.01)
    assert expected_thread_count(3)

    eww.remove()
    eww.remove()
    assert expected_thread_count(1)

    eww.embed(timeout=0.01)
    eww.embed(timeout=0.01)
    eww.remove()
    assert expected_thread_count(1)

def test_unregister_behavior():
    """Ensures proxies won't raise if I call unregister twice."""

    sys.stdin = eww.ioproxy.IOProxy(sys.stdin)

    sys.stdin.unregister()
    sys.stdin.unregister()

    sys.stdin = sys.stdin.original_file

    __builtin__.quit = eww.quitterproxy.QuitterProxy(__builtin__.quit)

    __builtin__.quit.unregister()
    __builtin__.quit.unregister()

    __builtin__.quit = __builtin__.quit.original_quit

def test_unregistered_quit():
    """Ensure we still quit if there isn't a quit handler registered."""

    __builtin__.quit = eww.quitterproxy.QuitterProxy(__builtin__.quit)
    __builtin__.quit.unregister()

    assert_raises(SystemExit, quit, 1)
    assert sys.stdin.closed == True

    # If we get here, the test passed, but we closed stdin.  Let's fix that.
    sys.stdin = open('/dev/tty')

    __builtin__.quit = __builtin__.quit.original_quit

def test_safe_quit():
    """Our safe quit function should raise SystemExit, but not close stdin."""

    __builtin__.quit = eww.quitterproxy.QuitterProxy(__builtin__.quit)
    __builtin__.quit.register(eww.quitterproxy.safe_quit)

    assert_raises(SystemExit, quit, 1)
    assert sys.stdin.closed == False

    __builtin__.quit = __builtin__.quit.original_quit

def test_bad_proxy_write():
    """Confirms we won't raise if a bad file is placed in IOProxy."""

    sys.stdin = eww.ioproxy.IOProxy(sys.stdin)

    sys.stdin.register(None)
    sys.stdin.write('This will not write, but should not raise.')

    sys.stdin = sys.stdin.original_file

def test_thread_death():
    """Embeds, then kills both threads to make sure we don't raise anything."""

    assert expected_thread_count(1)
    eww.embed(timeout=0.01)
    assert expected_thread_count(3)

    all_threads = threading.enumerate()
    eww_threads = []

    for thread in all_threads:
        if thread.name == DISPATCH_THREAD_NAME:
            eww_threads.append(thread)
        if thread.name == STATS_THREAD_NAME:
            eww_threads.append(thread)

    for thread in eww_threads:
        thread.stop()
        thread.join(5)

    assert expected_thread_count(1)

    # Make sure nothing is raised here
    eww.remove()
    assert expected_thread_count(1)

def test_socket_shutdown():
    """Embeds, connects to local console thread, then ensures the thread dies."""

    assert expected_thread_count(1)
    eww.embed(timeout=0.01)
    assert expected_thread_count(3)

    sock = connect_to_eww()
    assert expected_thread_count(expected=4)

    sock.shutdown(socket.SHUT_RDWR)
    sock.close()
    assert expected_thread_count(expected=3)

    eww.remove()
    assert expected_thread_count(1)

def test_console_kill():
    """Make sure we can kill a console thread."""

    assert expected_thread_count(1)
    eww.embed(timeout=0.01)
    assert expected_thread_count(3)

    sock = connect_to_eww()
    assert expected_thread_count(expected=4)

    # Find that little guy
    console_thread = None
    for thread in threading.enumerate():
        if '127.0.0.1' in thread.name:
            console_thread = thread
            break

    # Kill him
    console_thread.stop()
    assert expected_thread_count(expected=3)

    eww.remove()
    assert expected_thread_count(1)

    sock.close()

def test_default():
    """Ensures a proper default message is printed when invalid input is sent."""

    console = eww.command.Command()

    with CaptureOutput() as output:
        assert console.onecmd("Gahakafaka") == None
    assert output.stdout.getvalue() == "Command unrecognized.\n"

def test_console_quit():
    """Confirms the console sets quits correctly."""

    __builtin__.quit = eww.quitterproxy.QuitterProxy(__builtin__.quit)
    __builtin__.exit = eww.quitterproxy.QuitterProxy(__builtin__.exit)

    command = eww.command.Command.repl_command()
    command.register_quit()

    assert hasattr(__builtin__.quit.quit_routes, 'quit')
    assert hasattr(__builtin__.exit.quit_routes, 'quit')

    assert __builtin__.quit.quit_routes.quit == eww.quitterproxy.safe_quit
    assert __builtin__.exit.quit_routes.quit == eww.quitterproxy.safe_quit

    command.unregister_quit()

    assert hasattr(__builtin__.quit.quit_routes, 'quit') == False
    assert hasattr(__builtin__.exit.quit_routes, 'quit') == False

def test_console_exit():
    """Confirms the console can be exited via expected commands."""

    command = eww.command.Command()
    assert command.onecmd("exit") == True
    assert command.onecmd("quit") == True
    assert command.onecmd("EOF") == True

def test_baseCMD():
    """Confirms baseCMD exists and is structured as we expect."""

    command = eww.command.Command
    basecmd = command.BaseCmd()

    assert hasattr(basecmd, 'name')
    assert hasattr(basecmd, 'description')
    assert hasattr(basecmd, 'usage')
    assert hasattr(basecmd, 'options')
    assert type(basecmd.options) == list

    assert basecmd.run('foo') == None

def test_all_commands():
    """This enumerates all commands ensures they meet our basic
    requirements.
    """

    command = eww.command.Command()

    all_names = dir(command)

    command_names = []
    for name in all_names:
        if name.endswith('_command'):
            command_names.append(name)

    command_cls = []
    for name in command_names:
        command_cls.append(getattr(command, name))

    for cls in command_cls:
        assert hasattr(cls, 'name')
        assert hasattr(cls, 'description')
        assert hasattr(cls, 'usage')
        assert hasattr(cls, 'options')
        assert type(cls.options) == list
        assert hasattr(cls, 'run')

        assert callable(getattr(cls, 'run'))

def test_help_command():
    """Tests the help command."""

    command = eww.command.Command()

    all_names = dir(command)

    command_names = []
    for name in all_names:
        if name.endswith('_command'):
            command_names.append(name)

    help = command.help_command()

    assert len(help.get_commands()) == len(command_names) - 1  # Ignore EOF

    output = run_command(help)
    output = output.stdout
    output = output.split('\n')
    assert len(output) == 4 + len(command_names)

    output = run_command(help, 'Gahakafaka')
    output = output.stdout
    output = output.split('\n')
    assert len(output) == 2

    output = run_command(help, '-p blah')
    output = output.stdout
    assert output == 'no such option: -p\n'

    output = run_command(help, 'exit')
    output = output.stdout
    output = output.split('\n')
    assert 'Usage:' in output
    assert 'Description:' in output
    assert 'Options:' not in output

def test_onecmd():
    """Exercises a few onecmd parts that aren't frequently triggered."""

    command = eww.command.Command()

    # We just want to make sure these doesn't raise anything
    with CaptureOutput():
        command.parseline = Mock(return_value=(None, None, None))
        command.onecmd('')
        command.onecmd('bleeeehhh')

    with CaptureOutput():
        command.parseline = Mock(return_value=(None, None, 'None'))
        command.onecmd('')
        command.onecmd('bleeeehhh')

    with CaptureOutput():
        command.parseline = Mock(return_value=('', '', 'foo'))
        command.onecmd('')
        command.onecmd('bleeeehhh')

def test_repl():
    """Embeds eww, connects to repl, and then exits."""

    assert expected_thread_count(1)
    eww.embed(timeout=0.01)
    assert expected_thread_count(3)

    sock = connect_to_eww()
    assert expected_thread_count(4)

    assert sock_did_output(sock, '(eww)')
    sock.sendall('repl\n')
    assert sock_did_output(sock, '>>>')
    sock.sendall('exit\n')
    assert sock_did_output(sock, '(eww)')

    sock.shutdown(socket.SHUT_RDWR)
    sock.close()
    assert expected_thread_count(3)

    eww.remove()
    assert expected_thread_count(1)

def test_catchall_console():
    """This raises an exception in our console thread when we start it,
    that way we can verify the catchall exception will snatch things that
    may throw in cmdloop.
    """

    # Move proxies into place to shut console_thread up
    sys.stdin = eww.ioproxy.IOProxy(sys.stdin)
    sys.stdout = eww.ioproxy.IOProxy(sys.stdout)
    sys.stderr = eww.ioproxy.IOProxy(sys.stderr)

    # This is just a dummy socket so ConsoleThread's init is happy
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    console_thread = eww.console.ConsoleThread(sock)

    console_thread.start()

    # Let's make sure it's dead
    assert expected_thread_count(1)

    # Rip proxies back out
    sys.stdin = sys.stdin.original_file
    sys.stdout = sys.stdout.original_file
    sys.stderr = sys.stderr.original_file

def test_double_bind():
    """This ensures nothing goofy happens when our desired port is
    unavailable.
    """

    assert expected_thread_count(1)
    blocker_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    blocker_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    blocker_socket.bind(('localhost', 10001))
    blocker_socket.listen(5)

    eww.embed(timeout=0.01, port = 10001)
    assert expected_thread_count(2)

    blocker_socket.close()
    eww.remove()

def test_double_remove():
    """Tests we don't do anything goofy when someone tries to remove eww more
    than once simultaneously.
    """

    # Rather than try to trigger the race condition, we just set the removal
    # flag ourselves, and then as long as coverage shows we hit this branch
    # we're good.  This should probably be more clever.
    eww.shared.EMBEDDED.set()
    eww.shared.REMOVAL.set()
    eww.remove()
    eww.shared.REMOVAL.clear()
    eww.shared.EMBEDDED.clear()

def test_partial_removal():
    """Checks that we don't crash when some threads don't respond to removal
    request.
    """

    # This is also hacky.  We're going to grab a new thread, override it's
    # isAlive method (since that's how remove()) checks for 'liveness', then
    # use that as our 'unstoppable' thread.  In reality, the thread is dead,
    # the object just happens to always return true for isAlive()

    assert expected_thread_count(1)
    eww.embed(timeout=0.01)
    assert expected_thread_count(3)

    class LyingThread(eww.stoppable_thread.StoppableThread):
        """A thread that lies about whether it is alive or not."""

        def isAlive(self):
            return True

        def run(self):
            while True:
                if self.stop_requested:
                    return
                else:
                    time.sleep(0.01)

    lying_thread = LyingThread()
    lying_thread.daemon = True
    lying_thread.name = 'eww_lying_thread'
    lying_thread.start()
    assert expected_thread_count(4)

    eww.remove()
    assert expected_thread_count(1)

def test_stats_command():
    """Tests the stats command."""

    eww.shared.COUNTER_STORE.clear()
    eww.shared.GRAPH_STORE.clear()
    eww.shared.STATS_QUEUE.queue.clear()

    command = eww.command.Command()
    stats = command.stats_command()

    output = run_command(stats)
    output = output.stdout
    assert output == 'No stats recorded.\n'

    eww.shared.COUNTER_STORE['foo'] = 1

    output = run_command(stats)
    output = output.stdout
    assert output == 'Counters:\n  foo:1\n'

    output = run_command(stats, 'foo')
    output = output.stdout
    assert output == '1\n'

    eww.shared.COUNTER_STORE.clear()

    eww.shared.GRAPH_STORE['foo'] = deque()
    eww.shared.GRAPH_STORE['foo'].append((0,0))

    output = run_command(stats)
    output = output.stdout
    assert output == 'Graphs:\n  foo:1\n'

    output = run_command(stats, 'foo')
    output = output.stdout
    assert output == '[(0, 0)]\n'

    eww.shared.GRAPH_STORE.clear()

    output = run_command(stats, 'foo')
    output = output.stdout
    assert output == 'No stat recorded with that name.\n'

    output = run_command(stats, '-z foo')
    output = output.stdout
    assert output == 'no such option: -z\n'

    output = run_command(stats, '-t foo')
    output = output.stdout
    assert 'Usage' in output

    eww.shared.COUNTER_STORE.clear()
    eww.shared.GRAPH_STORE.clear()
    eww.shared.STATS_QUEUE.queue.clear()

def test_stats_graph():
    """Tests the graphing functions in stats."""

    eww.shared.COUNTER_STORE.clear()
    eww.shared.GRAPH_STORE.clear()
    eww.shared.STATS_QUEUE.queue.clear()

    command = eww.command.Command()
    stats = command.stats_command()

    eww.shared.GRAPH_STORE['foo1'] = deque()
    eww.shared.GRAPH_STORE['foo2'] = deque()

    for num in range(29):
        eww.shared.GRAPH_STORE['foo1'].append((num, num))

    for num in range(35):
        eww.shared.GRAPH_STORE['foo2'].append((num, num))

    run_command(stats, '-g foo1')
    run_command(stats, '-g foo2 -t foo2-chart')

    with open('foo1.svg') as foo1_file:
        foo1_svg = foo1_file.readlines()

    with open('foo2.svg') as foo2_file:
        foo2_svg = foo2_file.readlines()

    foo1_svg = ''.join(foo1_svg)
    foo2_svg = ''.join(foo2_svg)

    assert 'foo1' in foo1_svg
    assert 'foo2' in foo2_svg

    os.remove('foo1.svg')
    os.remove('foo2.svg')

    output = run_command(stats, '-g doesntexist')
    output = output.stdout
    assert output == 'No graph records exist for name doesntexist\n'

    output = run_command(stats, '-g foo1 -f /\\/\\\//')
    output = output.stdout
    assert 'Unable to write to' in output

    eww.shared.COUNTER_STORE.clear()
    eww.shared.GRAPH_STORE.clear()
    eww.shared.STATS_QUEUE.queue.clear()

def test_reduce_data():
    """Tests the reduce data function in the stats command."""

    command = eww.command.Command()
    stats = command.stats_command()

    list1 = list(range(59))
    list2 = list(range(60))
    list3 = list(range(61))

    assert len(stats.reduce_data(list1)) == stats.max_points
    assert len(stats.reduce_data(list2)) == stats.max_points
    assert len(stats.reduce_data(list3)) == stats.max_points

def test_counters():
    """Tests various counter functions."""

    eww.shared.COUNTER_STORE.clear()
    eww.shared.GRAPH_STORE.clear()
    eww.shared.STATS_QUEUE.queue.clear()

    stats_thread = eww.stats.StatsThread(max_datapoints=5, timeout=0.01)
    stats_thread.daemon = True
    stats_thread.start()

    assert not eww.shared.COUNTER_STORE

    eww.incr('foo1')
    eww.put('foo2')
    eww.decr('foo3', -1)

    assert expected_dict_size(eww.shared.COUNTER_STORE, 3)

    assert eww.shared.COUNTER_STORE['foo1'] == 1
    assert eww.shared.COUNTER_STORE['foo2'] == 1
    assert eww.shared.COUNTER_STORE['foo3'] == 1

    eww.incr('foo1')
    eww.put('foo2', 100)
    eww.decr('foo3')

    assert expected_counter_value('foo1', 2)
    assert expected_counter_value('foo2', 100)
    assert expected_counter_value('foo3', 0)

    eww.shared.GRAPH_STORE['graph_var'] = True
    eww.incr('graph_var')

    eww.shared.STATS_QUEUE.join()
    stats_thread.stop()
    assert expected_thread_count(1)

    bad_stat1 = eww.stats.Stat(name=1, type='counter', action='put', value=1)
    bad_stat2 = eww.stats.Stat(name='foo', type='counter', action='put', value='1')

    assert_raises(InvalidCounterOption,
                  eww.stats.counter_manipulation,
                  bad_stat1)
    assert_raises(InvalidCounterOption,
                  eww.stats.counter_manipulation,
                  bad_stat2)

    eww.shared.COUNTER_STORE.clear()
    eww.shared.GRAPH_STORE.clear()
    eww.shared.STATS_QUEUE.queue.clear()

def test_queue():
    """Tests that when a queue is full, nothing bad will happen."""

    eww.shared.COUNTER_STORE.clear()
    eww.shared.GRAPH_STORE.clear()
    eww.shared.STATS_QUEUE.queue.clear()

    for _ in range(600):
        eww.graph('queue_test1', (0, 0))

    for _ in range(200):
        eww.put('queue_test2')
        eww.incr('queue_test2')
        eww.decr('queue_test2')

    eww.shared.COUNTER_STORE.clear()
    eww.shared.GRAPH_STORE.clear()
    eww.shared.STATS_QUEUE.queue.clear()

def test_graphs():
    """Tests various graph functions."""

    eww.shared.COUNTER_STORE.clear()
    eww.shared.GRAPH_STORE.clear()
    eww.shared.STATS_QUEUE.queue.clear()

    stats_thread = eww.stats.StatsThread(max_datapoints=5, timeout=0.01)
    stats_thread.daemon = True
    stats_thread.start()

    assert_raises(InvalidGraphDatapoint, eww.graph, 1, (0, 0))
    assert_raises(InvalidGraphDatapoint, eww.graph, 'foo', 0)
    assert_raises(InvalidGraphDatapoint, eww.graph, 'foo', (0, 0, 0))
    assert_raises(InvalidGraphDatapoint, eww.graph, 'foo', ('f', 0))
    assert_raises(InvalidGraphDatapoint, eww.graph, 'foo', (0, 'f'))

    eww.graph('foo', (0, 0))
    assert expected_stat_exists('foo', 'graph')

    eww.shared.COUNTER_STORE['counter_var'] = True
    eww.graph('counter_var', (0, 0))
    eww.graph('sentinel', (0, 0))
    assert expected_stat_exists('sentinel', 'graph')

    stats_thread.stop()
    assert expected_thread_count(1)

    eww.shared.COUNTER_STORE.clear()
    eww.shared.GRAPH_STORE.clear()
    eww.shared.STATS_QUEUE.queue.clear()
