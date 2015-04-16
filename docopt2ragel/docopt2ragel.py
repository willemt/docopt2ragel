#!/usr/bin/env python
#-*- coding:utf-8 -*-

# Copyright (c) 2015 Willem Thiart
# Copyright (c) 2012 Vladimir Keleshev, <vladimir@keleshev.com>
# (see LICENSE file for copying)


"""Usage: docopt2ragel.py [<docopt>]

Processes a docopt formatted string from stdin.
Outputs Ragel code to parse the command line interface to stdout.

Arguments:
  <docopt>      Input file describing your CLI in docopt language.
"""


import sys
import os.path
import re
import docopt
from string import Template


def parse_section(name, source):
    pattern = re.compile('^([^\n]*' + name + '[^\n]*\n?(?:[ \t].*?(?:\n|$))*)',
                         re.IGNORECASE | re.MULTILINE)
    return [s.strip() for s in pattern.findall(source)]


def option_aliases(option):
    aliases = []
    if option.short:
        aliases.append(option.short)
    if option.long:
        aliases.append(option.long)
    return '({0})'.format(' | '.join(map(lambda a: "'{0}'".format(a), aliases)))


def clean_name(node):
    if hasattr(node, 'name'):
        return re.sub(r'[-<>]', r'', node.name)


def ragel_ast(node):
    cleaned_name = clean_name(node)
    if isinstance(node, docopt.Required):
        if hasattr(node, 'children'):
            return '({0})'.format(' '.join(map(ragel_ast, node.children)))
    elif isinstance(node, docopt.Either):
        return '({0})'.format(' | \n'.join(map(ragel_ast, node.children)))
    elif isinstance(node, docopt.Command):
        return "'{name}' 0 @command_{name}".format(name=cleaned_name)
    elif isinstance(node, docopt.Argument):
        return 'string 0 @argument_{name}'.format(name=cleaned_name)
    elif isinstance(node, docopt.Option):
        if 0 < node.argcount:
            return "{option} 0 string 0 @option_{name}".format(option=option_aliases(node), name=cleaned_name)
        else:
            return "{option} 0 @option_{name}".format(option=option_aliases(node), name=cleaned_name)
    elif isinstance(node, docopt.Optional):
        return '({0})*'.format(' '.join(map(ragel_ast, node.children)))
    assert False


def parse_leafs(pattern):
    leafs = []
    queue = [(0, pattern)]
    while queue:
        level, node = queue.pop(-1)  # depth-first search
        if hasattr(node, 'children'):
            children = [((level + 1), child) for child in node.children]
            children.reverse()
            queue.extend(children)
        else:
            if node not in leafs:
                leafs.append(node)
    leafs.sort(key=lambda e: e.name)
    commands = [leaf for leaf in leafs if type(leaf) == docopt.Command]
    arguments = [leaf for leaf in leafs if type(leaf) == docopt.Argument]
    flags = [leaf for leaf in leafs
             if type(leaf) == docopt.Option and leaf.argcount == 0]
    options = [leaf for leaf in leafs
               if type(leaf) == docopt.Option and leaf.argcount > 0]
    leafs = [i for sl in [commands, arguments, flags, options] for i in sl]
    return leafs, commands, arguments, flags, options


def main():
    args = docopt.docopt(__doc__)

    try:
        if args['<docopt>'] is not None:
            with open(args['<docopt>'], 'r') as f:
                args['<docopt>'] = f.read()
        elif args['<docopt>'] is None and sys.stdin.isatty():
            print(__doc__.strip("\n"))
            sys.exit("")
        else:
            args['<docopt>'] = sys.stdin.read()
    except IOError as e:
        sys.exit(e)

    doc = args['<docopt>']
    usage = parse_section('usage:', doc)
    s = ['More than one ', '"usage:" (case-insensitive)', ' not found.']
    usage = {0: s[1:], 1: usage[0] if usage else None}.get(len(usage), s[:2])
    if isinstance(usage, list):
        raise docopt.DocoptLanguageError(''.join(usage))

    options = docopt.parse_defaults(doc)

    pattern = docopt.parse_pattern(docopt.formal_usage(usage), options)

    fsm = ragel_ast(pattern)
    leafs, commands, arguments, flags, options = parse_leafs(pattern)

    command_fields = '\n    '.join(map(lambda c: 'int {0};'.format(clean_name(c)), commands))
    flag_fields = '\n    '.join(map(lambda c: 'int {0};'.format(clean_name(c)), flags))
    option_fields = '\n    '.join(map(lambda c: 'char* {0};'.format(clean_name(c)), options))
    argument_fields = '\n    '.join(map(lambda c: 'char* {0};'.format(clean_name(c)), arguments))

    command_actions = '\n    '.join(map(lambda c: 'action command_{0}{{ fsm->opt->{0} = 1; }}'.format(clean_name(c)), commands))
    flag_actions = '\n    '.join(map(lambda c: 'action option_{0}{{ fsm->opt->{0} = 1; }}'.format(clean_name(c)), flags))
    option_actions = '\n    '.join(map(lambda c: 'action option_{0}{{ fsm->opt->{0} = strdup(fsm->buffer); }}'.format(clean_name(c)), options))
    argument_actions = '\n    '.join(map(lambda c: 'action argument_{0}{{ fsm->opt->{0} = strdup(fsm->buffer); }}'.format(clean_name(c)), arguments))

    options_with_defaults = filter(lambda x: x.value is not None, options)
    option_defaults = '\n    '.join(map(lambda c: 'fsm->opt->{0} = strdup("{1}");'.format(clean_name(c), c.value), options_with_defaults))

    usage = '\n    '.join(map(lambda l: 'fprintf(stdout, "{0}\\n");'.format(l), doc.split('\n')))

    file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../template.rl")
    print Template(open(file).read()).safe_substitute(
        fsm=fsm,
        usage=usage,
        command_fields=command_fields,
        flag_fields=flag_fields,
        option_fields=option_fields,
        argument_fields=argument_fields,
        command_actions=command_actions,
        flag_actions=flag_actions,
        option_actions=option_actions,
        argument_actions=argument_actions,
        option_defaults=option_defaults,
        )

if __name__ == '__main__':
    main()
