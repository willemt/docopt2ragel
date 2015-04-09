docopt2ragel makes command line interface parsing easy!

docopt2ragel parses docopt USAGE text and outputs a Ragel finite state machine for parsing the CLI.

You can then use Ragel to output the finite state machine into C source code.

Example
=======

Create a USAGE file using docopt's declarative format. See below for example contents:

.. code-block:: bash

   dq - a command line tool for duraqueue the dead simple queue

   Usage:
     dq info <queue_file>
     dq --help

   Options:
     -h --help  Prints a short usage summary.

Convert the USAGE file into a Ragel file:

.. code-block:: bash

   docopt2ragel.py USAGE > usage.rl 

Convert the Ragel file into a C file:

.. code-block:: bash

   ragel usage.rl 

Import the generated file into your source:

.. code-block:: c

   #include "usage.c"

   int main(int argc, char **argv)
   {
       int e;
       options_t opts;

       e = parse_options(argc, argv, &opts);
       if (-1 == e)
       {
           exit(-1);
       }

       void *qu = NULL;

       if (opts.help)
       {
           show_usage();
           exit(0);
       }
       else if (opts.info)
       {
           qu = dqueuer_open(opts.queue_file);
       }

       if (qu)
           printf("Item count: %d\n", dqueue_count(qu));

       return 1;
   }


For real life examples see:

- https://github.com/willemt/duraqueue
- https://github.com/willemt/peardb

