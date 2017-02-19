#!/usr/bin/env python3
from functools import update_wrapper
import click


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
@click.option('--start', type=int, default=0)
@generator
def makeints(start):
    while True:
        start = start + 1
        if start > 3:
            quit(0)
        yield start

@cli.command('display')
@processor
def display(someints):
    print("entering display()")
    for someint in someints:
        print("display() someint:", someint) #why does this not print when view() calls ctx.forward(display)?
        yield someint

@cli.command('view')
@processor
def view(someints):
#    ctx = click.get_current_context()
#    ctx.forward(display)
    for someint in someints:
        print("view() someint:", someint)
        ctx = click.get_current_context()
        ctx.forward(display)
        yield someint


@cli.command()
@click.option('--count', default=1)
def test(count):
    click.echo('Count: %d' % count)

@cli.command()
@click.option('--count', default=1)
@click.pass_context
def dist(ctx, count):
    ctx.forward(test)
    ctx.invoke(test, count=42)

#if __name__ == '__main__':
#    #dist()
#    makeints()

