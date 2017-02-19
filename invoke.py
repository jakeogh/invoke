#!/usr/bin/env python3
from functools import update_wrapper
import click

# attempt to use http://click.pocoo.org/6/advanced/#invoking-other-commands
# with command chain like https://github.com/pallets/click/blob/master/examples/imagepipe/imagepipe.py
#
# Install:
# git clone https://github.com/jakeogh/invoke.git
# python setup.py install
#
# Usage:
# invoke makeints view     # this should call disp() via ctx.forward(disp) but it does not
# invoke makeints disp     # this works as expected
#
# Actual output:
#
# $ invoke makeints view
# view() someint: 1
# view() someint: 2
# view() someint: 3
#
# Desired output:
#
# $ invoke makeints view
# view() someint: 1
# disp() someint: 1
# view() someint: 2
# disp() someint: 2
# view() someint: 3
# disp() someint: 3

# Note:
# $ invoke makeints disp view
# # works as expected


@click.group(chain=True)
def cli():
    """
        test
    """
@cli.resultcallback()
def process_commands(processors):
    """This result callback is invoked with an iterable of all the chained
    subcommands.  As in this example each subcommand returns a function
    we can chain them together to feed one into the other, similar to how
    a pipe on unix works.
    """
    # Start with an empty iterable.
    stream = ()

    # Pipe it through all stream processors.
    for processor in processors:
        stream = processor(stream)

    # Evaluate the stream and throw away the items.
    for _ in stream:
        pass

def processor(f):
    """Helper decorator to rewrite a function so that it returns another
    function from it.
    """
    def new_func(*args, **kwargs):
        def processor(stream):
            return f(stream, *args, **kwargs)
        return processor
    return update_wrapper(new_func, f)

def generator(f):
    """Similar to the :func:`processor` but passes through old values
    unchanged and does not pass through the values as parameter.
    """
    @processor
    def new_func(stream, *args, **kwargs):
        for item in stream:
            yield item
        for item in f(*args, **kwargs):
            yield item
    return update_wrapper(new_func, f)

@cli.command('makeints')
@generator
def makeints(start=0):
    while True:
        start = start + 1
        if start > 3:
            quit(0)
        yield start

@cli.command('disp')
@processor
def disp(someints):
    for someint in someints:
        print("disp() someint:", someint) #why does this not print when view() calls ctx.forward(disp)?
        yield someint

@cli.command('view')
@processor
def view(someints):
    for someint in someints:
        print("view() someint:", someint)
        ctx = click.get_current_context()
        #from pudb import set_trace; set_trace()
        ctx.forward(disp) #why does this not call display()?
        yield someint

## working ctx.invoke and ctx.forward example
## $ invoke dist
## 1
## 42
#
#@cli.command()
#@click.option('--count', default=1)
#def test(count):
#    click.echo('Count: %d' % count)
#
#@cli.command()
#@click.option('--count', default=1)
#@click.pass_context
#def dist(ctx, count):
#    ctx.forward(test)
#    ctx.invoke(test, count=42)
