Title: Haskell-Style Fibonacci in Python
Date: 2015-07-07 12:00
Category: Mathematics, Code, Haskell, Python

If you've ever done a tech interview, you're probably familiar
with the Fibonacci sequence:

1, 1, 2, 3, 5, 8, 13, ....

where each number is the sum of the previous two.  A relatively simple
(and relatively overused)
interview problem is to write a function that returns the n-th
Fibonacci number.

<h2>Recursive Python</h2>

The most intuitive implementation is recursive:

```python
def fib(n):
  """the profoundly inefficient recursive implementation"""
  if n in [0, 1]:
    return 1
  else:
    return fib(n - 1) + fib(n - 2)
```

It works in a pretty obvious fashion.

```python
>>> map(fib, range(10))
[1, 1, 2, 3, 5, 8, 13, 21, 34, 55]
```

However, it's shockingly inefficient.
To compute `fib(10)` we need to compute `fib(9)` and `fib(8)`.  To compute
`fib(9)` we need to compute `fib(8)` (again) and `fib(7)`.  And so on.

The moral of the story is that to compute `fib(10)` we end up making 177
calls to `fib`.  To compute `fib(20)` we end up making 21,891 calls to `fib`.
And to compute `fib(30)` we end up making 2.7 million calls to `fib`, which
ends up taking almost a full second on my laptop.

One solution is <a href="https://en.wikipedia.org/wiki/Memoization">memoization</a>,
in which we remember previously computed values.  We won't get into that here.

<h2>Iterative Python</h2>

Another solution is an iterative approach:

```python
def fib(n):
  """the iterative implementation"""
  x, y = 0, 1
  for _ in range(n):
    x, y = y, x + y
  return y
```

This is much more efficient -- to compute `fib(n)` we just do O(n) operations.
At the same time, it's much less clear what it's actually computing.
If I didn't tell you it was `fib`
you might have to stare at it for a while to figure out exactly what it was doing.
And even knowing that it's `fib` it's probably not obvious that it's
implemented *correctly*.

<h2>Haskell</h2>

Haskell, in case you don't know, is everyone's favorite pure functional
programming language.  In particular, it embraces
<a href="https://en.wikipedia.org/wiki/Lazy_evaluation">laziness</a>
in which values are computed only as needed.  

This means we can compute <a href="https://wiki.haskell.org/The_Fibonacci_sequence#Canonical_zipWith_implementation">the (infinite) sequence of Fibonacci numbers</a> as

```haskell
fibs :: [Int]
fibs = 1 : 1 : zipWith (+) fibs (tail fibs)

Prelude> take 10 fibs
[1,1,2,3,5,8,13,21,34,55]
```

You should understand this definition as "the sequence that starts with 1,
followed by 1,
followed by the sequence of numbers
obtained by "zipping" together the sequences `fibs` and `tail fibs`
(that is, all of the elements of `fibs` after the first)
and adding together each corresponding pair of elements.  

Which means the third element of the sequence is the first element (of `fibs`) plus
the second element (which is the first element of `tail fibs`).  The fourth element
is the second element (of `fibs`) plus the third element (which is the second element
of `tail fibs`).  And so on.  This is precisely the definition of Fibonacci.

This definition may seem circular, since we're using `fibs` to define `fibs`.

After all, the following sort of thing leads to infinite recursion:

```python
def fibs(x=0, y=1):
  return [y] + fibs(y, x+y)

>>> fibs()[0]
....
RuntimeError: maximum recursion depth exceeded
```

But in the Haskell version, because of laziness, the elements of `fibs` will only be evaluated as needed.
To compute the third element, we only need to know the first two elements,
which we already do by the time we're trying to compute the third element, and so on.

Appreciate its stark, mathematical beauty!  (Learn Haskell!)

<h2>Laziness in Python</h2>

We can achieve laziness in Python using generators.  One way is list comprehensions
in parentheses.

```python
>>> num = (i for i in range(3))
>>> num
<generator object <genexpr> at 0x7f5efc33bd70>
>>> num.next()
0
>>> num.next()
1
>>> num.next()
2
>>> num.next()
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
StopIteration
```

Each element of `num` is computed only on demand.

We can also use functions with `yield`:

```python
>>> def to3():
...   yield 1
...   yield 2
...   yield 3
...
>>> [x for x in to3()]
[1, 2, 3]
```

This is how we'll implement the Haskell-style Fibonacci.

<h2>itertools</h2>

The Haskell implementation used `tail` (to get the elements after the first)
and `take` (to get a certain number of elements from the front).  Python
doesn't have those, so we'll need
to implement our own versions.

The `itertools` module contains some helpers for working with laziness.
We'll need `islice` which allows us to slice a new generator out of an old one.

```python
from itertools import islice

def tail(iterable):
  """return elements from 1 to forever"""
  return islice(iterable, 1, None)

def take(n, iterable):
  """return elements from 0 to n in a list"""
  return list(islice(iterable, 0, n))
```

For our Python 2.7 version we'll also need `imap`, which is simply the lazy version of `map`.

As a warmup, let's create an infinite sequence using the iterative approach:

```python
def fibs():
  x, y = (0, 1)
  while True:
    yield y
    (x, y) = (y, x + y)
```

Which we can use like:

```python
>>> take(10, fibs())
[1, 1, 2, 3, 5, 8, 13, 21, 34, 55]
```

<h2>Haskell-style in Python</h2>

Recall the Haskell implementation:

```haskell
fibs = 1 : 1 : zipWith (+) fibs (tail fibs)
```

It's not hard to create the Python 2.7 equivalent

```python
from itertools import imap   # lazy map
from operator import add     # add(x, y) = x + y

def fibs():
  yield 1
  yield 1
  for n in imap(add, fibs(), tail(fibs())):
    yield n
```

The logic is exactly the same.  The first two elements both equal 1.
After that we lazily add together the corresponding elements of `fibs()`
and of `tail(fibs())`:

```python
>>> take(10, fibs())
[1, 1, 2, 3, 5, 8, 13, 21, 34, 55]
```

In Python 3.3+, this gets even simpler.  First `map` is already lazy,
so there's no reason to use `imap`.  And second, 3.3 introduces
<a href="https://docs.python.org/3/whatsnew/3.3.html#pep-380">`yield from`</a>
which allows us to replace the clunky

```python
for x in xs:
  yield x
```

with

```python
yield from xs
```

This means that the Python 3.3+ implementation is simply:

```python
def fibs():
  yield 1
  yield 1
  yield from map(add, fibs(), tail(fibs()))
```

Which we could one-line as

```python
def fibs(): yield 1; yield 1; yield from map(add, fibs(), tail(fibs()))
```

More on this in a second.

<h2>Warning!</h2>

Despite appearing Haskell-like, this version is basically as inefficient
as the original recursive version.  That's because every time `fibs()`
is called recursively, Python redoes from scratch all the work to generate
the sequence.  

Whereas in Haskell things are
<a href="https://wiki.haskell.org/Functional_programming#Immutable_data">immutable</a>,
which means that there's
only a single `fibs` hanging around.  Once its first few elements have been
computed, they never have to be computed again.

So while our Python version is clever, it's also impractical.

<h2>A Final Comparison</h2>

Compare again

```python
def fibs(): yield 1; yield 1; yield from map(add, fibs(), tail(fibs()))
```

with the Haskell

```haskell
fibs = 1 : 1 : zipWith (+) fibs (tail fibs)
```

It's practically the same code!  (Yes, the one-line version is hideous Python,
I just did that so it would be more comparable with the Haskell version.)

I showed it to one of my friends, who was so impressed that he said
"I have no idea what that Python code does".

Next time you get asked Fibonacci as an interview question,
consider using this version, and let me know what happens!

<h2>Update!!!!!!</h2>

As was pointed out in the comments, one can use `itertools.tee` to split a
generator into multiple (efficient) copies.  This means that the following
slight modification:

```python
def fibs():
  print("a new fibs")
  yield 1
  yield 1
  fibs1, fibs2 = tee(fibs())
  yield from map(add, fibs1, tail(fibs2))
```

is incredibly efficient. 
