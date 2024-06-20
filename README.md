# Unified register API

Generic register sharing API across a tree of register-holding services.

## Concepts and Terminology

### Registers

Registers are storage locations used for copy-paste. In `tmux`, this concept is
called _buffers_, which conflicts with the `vim` idea of buffers... so I went
with registers to match `vim`.

`tmux` has special numbered buffers, as does `vim`, but those are not covered by
this API as manipulating them in a way that makes sense for both programs would
be challenging. `tmux` supports arbitrarily named buffers, but `vim` only
supports [a-z], unnamed, and OS registers. The OS registers (copy and selection)
should be handled by a dedicated tool for interacting with the OS (e.g. OSC esc
codes).

With this background, this API supports the following register names:
- Single-character, lowercase alphabetic characters [a-z]
- The special register "unnamed"

## API

`reg [--instance <instance>] <command> [<command options and args]`

### Direct register manipulation

#### get

#### list

#### set

#### delete
