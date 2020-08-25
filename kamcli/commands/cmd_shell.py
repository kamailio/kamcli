##
# Adapted from: https://github.com/click-contrib/click-repl
#
# Copyright (c) 2014-2015 Markus Unterwaditzer & contributors
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# kamcli specific code - Copyright (c) 2020 Daniel-Constantin Mierla
#


import click
import click._bashcomplete
import click.parser
from kamcli.cli import pass_context
from collections import defaultdict
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.shortcuts import prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.styles import Style
from prompt_toolkit.lexers import PygmentsLexer
from pygments.lexers.shell import BashLexer
import os
import shlex
import sys


class InternalCommandException(Exception):
    pass


class ExitReplException(InternalCommandException):
    pass


# Handle click.exceptions.Exit introduced in Click 7.0
try:
    from click.exceptions import Exit as ClickExit
except ImportError:

    class ClickExit(RuntimeError):
        pass


# Dictionary with internal commands of the interactive shell
_internal_commands = dict()


def _register_internal_command(names, target, description=None):
    if not hasattr(target, "__call__"):
        raise ValueError("Internal command must be a callable")

    if isinstance(names, str):
        names = [names]
    elif not isinstance(names, (list, tuple)):
        raise ValueError('"names" must be a string or a list / tuple')

    for name in names:
        _internal_commands[name] = (target, description)


def _get_registered_target(name, default=None):
    target_info = _internal_commands.get(name)
    if target_info:
        return target_info[0]
    return default


def _exit_internal():
    raise ExitReplException()


def _help_internal():
    formatter = click.HelpFormatter()
    formatter.write_heading("Interactive Shell Help")
    formatter.indent()
    with formatter.section("Kamcli Commands"):
        formatter.write_text(
            "- type the command followed by options and parameters"
        )
        formatter.write_text("- example: db show version")
        formatter.write_text(
            "- <tab> - completion window with options and subcommands"
        )
        formatter.write_text("- ? - kamcli help")
    with formatter.section("External Shell Commands"):
        formatter.write_text('- prefix external commands with "!"')
        formatter.write_text("- example: !ls -la")
    with formatter.section("Internal Shell Commands"):
        formatter.write_text('- prefix internal commands with ":" or "/"')
        formatter.write_text("- example: :exit")
        formatter.write_text("- example: /exit")
        formatter.write_text("- available internal commands:")
        for mnemonic, target_info in _internal_commands.items():
            formatter.write_dl(
                [("    * " + mnemonic + " -", target_info[1])], col_spacing=2
            )

    return formatter.getvalue()


_register_internal_command(
    ["q", "quit", "exit"], _exit_internal, "exit the interactive shell"
)
_register_internal_command(
    ["?", "h", "help"], _help_internal, "displays general help information"
)


class ClickCompleter(Completer):
    def __init__(self, cli):
        self.cli = cli

    def get_completions(self, document, complete_event=None):
        # Code analogous to click._bashcomplete.do_complete

        try:
            args = shlex.split(document.text_before_cursor)
        except ValueError:
            # Invalid command, perhaps caused by missing closing quotation.
            return

        cursor_within_command = (
            document.text_before_cursor.rstrip() == document.text_before_cursor
        )

        if args and cursor_within_command:
            # We've entered some text and no space, give completions for the
            # current word.
            incomplete = args.pop()
        else:
            # We've not entered anything, either at all or for the current
            # command, so give all relevant completions for this context.
            incomplete = ""

        ctx = click._bashcomplete.resolve_ctx(self.cli, "", args)
        if ctx is None:
            return

        choices = []
        for param in ctx.command.params:
            if isinstance(param, click.Option):
                for options in (param.opts, param.secondary_opts):
                    for o in options:
                        choices.append(
                            Completion(
                                str(o),
                                -len(incomplete),
                                display_meta=param.help,
                            )
                        )
            elif isinstance(param, click.Argument):
                if isinstance(param.type, click.Choice):
                    for choice in param.type.choices:
                        choices.append(
                            Completion(str(choice), -len(incomplete))
                        )

        if isinstance(ctx.command, click.MultiCommand):
            for name in ctx.command.list_commands(ctx):
                command = ctx.command.get_command(ctx, name)
                choices.append(
                    Completion(
                        str(name),
                        -len(incomplete),
                        display_meta=getattr(command, "short_help"),
                    )
                )

        for item in choices:
            if item.text.startswith(incomplete):
                yield item


def bootstrap_prompt(prompt_kwargs, group):
    """
    Bootstrap prompt_toolkit kwargs or use user defined values.

    :param prompt_kwargs: The user specified prompt kwargs.
    """
    prompt_kwargs = prompt_kwargs or {}

    defaults = {
        "history": InMemoryHistory(),
        "completer": ClickCompleter(group),
        "message": [("class:prompt", "kamcli > "),],
        "style": Style.from_dict({"prompt": "bold",}),
        "auto_suggest": AutoSuggestFromHistory(),
    }

    for key in defaults:
        default_value = defaults[key]
        if key not in prompt_kwargs:
            prompt_kwargs[key] = default_value

    return prompt_kwargs


def shell_repl(
    old_ctx,
    prompt_kwargs=None,
    allow_system_commands=True,
    allow_internal_commands=True,
):
    """
    Start an interactive shell. All subcommands are available in it.

    :param old_ctx: The current Click context.
    :param prompt_kwargs: Parameters passed to
        :py:func:`prompt_toolkit.shortcuts.prompt`.

    If stdin is not a TTY, no prompt will be printed, but only commands read
    from stdin.

    """
    # parent should be available, but we're not going to bother if not
    group_ctx = old_ctx.parent or old_ctx
    group = group_ctx.command
    isatty = sys.stdin.isatty()

    # name of the shell command to skip if executed inside the shell.
    shell_command_name = old_ctx.command.name

    prompt_kwargs = bootstrap_prompt(prompt_kwargs, group)

    if isatty:

        def get_command():
            return prompt(**prompt_kwargs)

    else:
        get_command = sys.stdin.readline

    click.echo("Quick help:")
    click.echo("  ?  - kamcli commands help")
    click.echo("  :h - internal commands help")
    click.echo("  :q - quit interactive shell")
    click.echo("  -- ")

    while True:
        try:
            command = get_command()
        except KeyboardInterrupt:
            continue
        except EOFError:
            break

        if not command:
            if isatty:
                continue
            else:
                break

        if allow_system_commands and dispatch_repl_commands(command):
            continue

        if allow_internal_commands:
            try:
                result = handle_internal_commands(command)
                if isinstance(result, str):
                    click.echo(result)
                    continue
            except ExitReplException:
                break

        try:
            args = shlex.split(command)
        except ValueError as e:
            click.echo("{}: {}".format(type(e).__name__, e))
            continue

        if shell_command_name == args[0]:
            click.echo(
                "error: recurrent execution of '{}' subcommand".format(
                    shell_command_name
                )
            )
            continue

        try:
            with group.make_context(None, args, parent=group_ctx) as ctx:
                group.invoke(ctx)
                ctx.exit()
        except click.ClickException as e:
            e.show()
        except ClickExit:
            pass
        except SystemExit:
            pass
        except ExitReplException:
            break


def exit():
    """Exit the repl"""
    _exit_internal()


def dispatch_repl_commands(command):
    """Execute system commands entered in the repl.

    System commands are all commands starting with "!".

    """
    if command.startswith("!"):
        os.system(command[1:])
        return True

    return False


def handle_internal_commands(command):
    """Run repl-internal commands.

    Repl-internal commands are all commands starting with ":".

    """
    if command.startswith(":") or command.startswith("/"):
        target = _get_registered_target(command[1:], default=None)
        if target:
            return target()


@click.command("shell", short_help="Run in interactive shell mode")
@click.option(
    "nohistory",
    "--no-history",
    "-N",
    is_flag=True,
    help="Do not save commands history",
)
@click.option(
    "nosyntax",
    "--no-syntax",
    "-S",
    is_flag=True,
    help="Do not enable syntax highlighting for command line",
)
@pass_context
def cli(ctx, nohistory, nosyntax):
    """Run in shell mode

    \b
    """
    prompt_kwargs = {}

    if not nohistory:
        prompt_kwargs.update(
            {"history": FileHistory(os.path.expanduser("~/.kamcli/history"))}
        )

    if not nosyntax:
        prompt_kwargs.update({"lexer": PygmentsLexer(BashLexer)})

    shell_repl(click.get_current_context(), prompt_kwargs=prompt_kwargs)
