Due to []-operation being exactly car/cdr, you have to make the following changes to your
backports before we implement car/cdr in castrated python:

```
<   return (lcg_seed(state[0]), (direction, state[1][1]+1))
---
>   return (lcg_seed(state[0]), direction, state[2:]+1)
```

===


Remember that sometimes when we use overflows from castrated world, python's long arithmetic
will yield different behaviour, hence we need to do mod 2^32 to fix that:

```
< import math
*snip*
<   return (seed * 1664525 + 1013904223) % int(math.pow(2, 32))
---
>   return (seed * 1664525 + 1013904223)
```

===


Remember that for now int() has different semantics in castrated python, it actually translates
to ATOM. Probably will be fixed during the next hacking cycle of the castrated python.

===


Here's how we initialize main:

```
sstate, _step = main(someworld, 0)
```

Preserving state between calls in python:

```
sstate, direction = step(sstate, 0)
```
