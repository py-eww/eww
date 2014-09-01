# -*- coding: utf-8 -*-
"""
    eww.command
    ~~~~~~~~~~~

    This is our custom command module.  It is a subclass of
    :py:class:`cmd.Cmd`.  The most significant change is using classes rather
    than functions for the commands.

    Due to this change, we don't use CamelCase for command class names here.
    Strictly that's ok via PEP8 since we are kinda treating these like
    callables.  Just a heads up.

"""
# PyLint picks up a lot of things here that it shouldn't.  We clean up here.
# pylint: disable=too-few-public-methods, no-self-use, invalid-name
# pylint: disable=too-many-public-methods, redefined-outer-name
# pylint: disable=maybe-no-member, no-member, star-args, bad-builtin

import cmd
import code
import logging
from math import ceil
import os
import shlex
from StringIO import StringIO
import sys
import __builtin__

try:
    import pygal
except ImportError:  # pragma: no cover
    # Just in case pygal isn't installed
    pass

from .parser import Parser, ParserError, Opt
from .quitterproxy import safe_quit
from .shared import COUNTER_STORE, GRAPH_STORE

LOGGER = logging.getLogger(__name__)

class Command(cmd.Cmd):
    """Our cmd subclass where we implement all console functionality."""

    class BaseCmd(object):
        """The base class for all commands."""

        # You should define the following properties on all subclasses
        name = 'Undefined'
        description = 'Undefined'
        usage = 'Undefined'
        options = []

        def run(self, line):
            """Performs the requested command.  You should definitely override
            this.

            Args:
                line (str): A command line argument to be parsed.

            Returns:
                bool: True to exit, None otherwise.
            """
            pass

    class EOF_command(BaseCmd):
        """Implements support for EOF being interpreted as an exit request."""

        name = 'EOF'
        description = 'An EOF will trigger this command and exit the console.'
        usage = 'N/A'

        def run(self, line):
            """Returns True to trigger an exit.

            Args:
                line (str): A command line argument to be parsed.

            Returns:
                bool: True
            """
            return True

    class exit_command(BaseCmd):
        """Implements support for the 'exit' command to leave the console."""

        name = 'exit'
        description = 'Exits the console. (same as quit)'
        usage = 'exit'

        def run(self, line):
            """Returns True to trigger an exit.

            Args:
                line (str): A command line argument to be parsed.

            Returns:
                bool: True
            """
            return True

    class quit_command(BaseCmd):
        """Implements support for the 'quit' command to leave the console."""

        name = 'quit'
        description = 'Quits the console. (same as exit)'
        usage = 'quit'

        def run(self, line):
            """Returns True to trigger an exit.

            Args:
                line (str): A command line argument to be parsed.

            Returns:
                bool: True
            """
            return True

    class repl_command(BaseCmd):
        """Drops the user into a python REPL."""

        name = 'repl'
        description = 'Provides an interactive REPL.'
        usage = 'repl'

        def register_quit(self):
            """Registers our custom quit function to prevent stdin from being
            closed.

            Returns:
                None
            """
            __builtin__.quit.register(safe_quit)
            __builtin__.exit.register(safe_quit)

        def unregister_quit(self):
            """Unregisters our custom quit function.

            Returns:
                None
            """
            __builtin__.quit.unregister()
            __builtin__.exit.unregister()

        def run(self, line):
            """Implements the repl.

            Args:
                line (str): A command line argument to be parsed.

            Returns:
                None
            """

            print 'Dropping to REPL...'

            repl = code.InteractiveConsole()

            try:
                self.register_quit()
                banner = 'Python ' + sys.version + ' on ' + sys.platform + '\n'
                banner += 'Note: This interpreter is running *inside* of your '
                banner += 'application.  Be careful.'
                repl.interact(banner)
            except SystemExit:
                # This catches the exit or quit from the REPL.
                pass
            finally:
                self.unregister_quit()

            print "Exiting REPL..."

    class stats_command(BaseCmd):
        """A command for inspecting stats and generating graphs."""

        name = 'stats'
        description = 'Outputs recorded stats and generates graphs.'
        usage = 'stats [args] [stat_name]'

        # Declare options
        options = []
        options.append(Opt('-g', '--graph',
                           dest='graph',
                           default=False,
                           action='store_true',
                           help='Create graph'))
        options.append(Opt('-f', '--file',
                           dest='file',
                           default=False,
                           action='store',
                           type='string',
                           help='Filename to use when saving graph'))
        options.append(Opt('-t', '--title',
                           dest='title',
                           default=False,
                           action='store',
                           type='string',
                           help='Graph title'))

        def __init__(self):
            """Init."""
            super(Command.stats_command, self).__init__()

            self.parser = Parser()
            self.parser.add_options(self.options)

            # Pygal won't support more than this currently
            self.max_points = 30

        def display_stat_summary(self):
            """Prints a summary of collected stats.

            Returns:
                None
            """

            if not COUNTER_STORE and not GRAPH_STORE:
                print "No stats recorded."
                return

            if COUNTER_STORE:
                print "Counters:"
                for stat in COUNTER_STORE:
                    print " ", stat + ':' + str(COUNTER_STORE[stat])

            if GRAPH_STORE:
                print "Graphs:"
                for stat in GRAPH_STORE:
                    print " ", stat + ':' + str(len(GRAPH_STORE[stat]))

        def display_single_stat(self, stat_name):
            """Prints a specific stat.

            Args:
                stat_name (str): The stat name to display details of.

            Returns:
                None
            """

            if stat_name in COUNTER_STORE:
                print COUNTER_STORE[stat_name]
                return

            if stat_name in GRAPH_STORE:
                print list(GRAPH_STORE[stat_name])
                return

            else:
                print 'No stat recorded with that name.'

        def reduce_data(self, data):
            """Shrinks len(data) to ``self.max_points``.

            Args:
                data (iterable): An iterable greater than ``self.max_points``.

            Returns:
                list: A list with a fair sampling of objects from ``data``,
                      and a length of ``self.max_points.``
            """

            # Thanks to Adam Forsyth for this implementation
            shrunk = []
            size = float(len(data))

            for num in range(self.max_points):
                shrunk.append(data[int(ceil(num * size / self.max_points))])

            return shrunk

        def generate_graph(self, options, stat_name):
            """Generate a graph of ``stat_name``.

            Args:
                options (dict): A dictionary of option values generated from
                                our parser.
                stat_name (str): A graph name to create a graph from.

            Returns:
                None
            """

            if stat_name not in GRAPH_STORE:
                print 'No graph records exist for name', stat_name
                return

            if 'pygal' not in sys.modules:  # pragma: no cover
                print 'Pygal library unavailable.  Try running `pip install',
                print 'pygal`.'
                return

            data = list(GRAPH_STORE[stat_name])
            graph = pygal.Line()

            if options['title']:
                graph.title = options['title']
            else:
                graph.title = stat_name

            if len(data) > self.max_points:
                data = self.reduce_data(data)

            x_labels, y_labels = zip(*data)
            graph.x_labels = map(str, x_labels)
            graph.add(stat_name, y_labels)

            graph_svg = graph.render()

            filename = options['file'] or stat_name
            filename += '.svg'

            try:
                with open(filename, 'w') as svg_file:
                    svg_file.write(graph_svg)
                    print 'Chart written to', filename  # pragma: no cover
            except IOError:
                print 'Unable to write to', os.getcwd() + '/' + filename

        def run(self, line):
            """Outputs recorded stats and generates graphs.

            Args:
                line (str): A command line argument to be parsed.

            Returns:
                None
            """
            if not line:
                self.display_stat_summary()
                return

            try:
                options, remainder = self.parser.parse_args(shlex.split(line))
            except ParserError as error_msg:
                print error_msg
                return

            options = vars(options)

            if not remainder:
                # User entered something goofy
                help_cmd = Command.help_command()
                help_cmd.display_command_detail('stats')
                return

            if options['graph']:
                self.generate_graph(options, remainder[0])
                return
            else:
                self.display_single_stat(remainder[0])
                return

    class help_command(BaseCmd):
        """When called with no arguments, this presents a friendly help page.
        When called with an argument, it presents command specific help.
        """

        name = 'help'
        description = 'help provides in-console documentation.'
        usage = 'help [command]'

        # Declare options
        options = []

        def __init__(self):
            """Init."""
            super(Command.help_command, self).__init__()

            self.parser = Parser()
            self.parser.add_options(self.options)

        def get_commands(self):
            """Returns a list of command classes.

            Returns:
                list: A list of command classes (not instantiated).
            """

            commands = []
            blacklist = ['EOF_command']

            # First we get a list of all command names
            all_names = dir(Command)

            # Then find on-topic names
            for name in all_names:
                if name.endswith('_command') and name not in blacklist:
                    # Pull names and descriptions
                    cls = getattr(Command, name)
                    commands.append(cls)

            return commands

        def display_commands(self):
            """Displays all included commands.

            Returns:
                None
            """

            commands = self.get_commands()

            print 'Available Commands:'
            print ''
            for command in commands:
                print ' ', command.name, '-', command.description
            print ''
            print 'For more info on a specific command, enter "help <command>"'

        def display_command_detail(self, command_name):
            """Displays detailed command help.

            Args:
                command_name (str): A command name to print detailed help for.

            Returns:
                None
            """

            name = command_name + '_command'
            try:
                cls = getattr(Command, name)
            except AttributeError:
                print command_name, 'is not a valid command.'
                return

            print 'Usage:'
            print ' ', cls.usage
            print ''
            print 'Description:'
            print ' ', cls.description

            if not cls.options:
                # All done
                return
            else:
                print ''

            # There are a lot of edge cases around pretty printing options.
            # This is not elegant, but it's the least brittle option.
            output = StringIO()

            parser = Parser()
            parser.add_options(cls.options)
            parser.print_help(file=output)

            output = output.getvalue()

            # Massage output
            output = output.split('\n')
            # Remove trailing newline
            output = output[:-1]
            # Print everything after Options
            start = output.index('Options:')
            for line in output[start:]:
                print line

        def run(self, line):
            """Provides help documentation.

            Args:
                line (str): A command line argument to be parsed.

            Returns:
                None
            """

            if not line:
                self.display_commands()
                return

            try:
                options, remainder = self.parser.parse_args(shlex.split(line))
                del options  # To shutup pylint
            except ParserError as error_msg:
                print error_msg
                return

            self.display_command_detail(remainder[0])

    def onecmd(self, line):
        """We override cmd.Cmd.onecmd in order to support our class-based
        commands.  Changes are noted via comments.

        Args:
            line (str): A command (with arguments) to be executed.

        Returns:
            bool: True if a command is designed to exit, otherwise None.
        """

        cmd, arg, line = self.parseline(line)
        if not line:
            return self.emptyline()
        if cmd is None:
            return self.default(line)
        self.lastcmd = line
        if line == 'EOF':
            self.lastcmd = ''
        if cmd == '':
            return self.default(line)
        else:
            try:
                # Changes start
                cmd_class = getattr(Command, cmd + '_command')
                cmd_class = cmd_class()
                # Changes end
            except AttributeError:
                return self.default(line)
            # Changes start
            return cmd_class.run(arg)
            # Changes end

    def default(self, line):
        """The first responder when a command is unrecognized."""
        print 'Command unrecognized.'
