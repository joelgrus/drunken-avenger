Title: On The Mathematics of Spot It!
Date: 2015-06-12 12:00
Category: Mathematics, Code, Spot it, Madeline, Frozen

Last weekend we went to a party where one of the other attendees brought
<a href = "http://www.amazon.com/Spot-it-Disney-Frozen-Alphabet/dp/B00LK0N1ZK">Spot It! Frozen</a> 
for her kids. It's a simple game with circular cards, each of which has 8 pictures in it,
most of them <i>Frozen</i>-themed.

![frozen]({filename}images/spot_it_frozen.jpg)

The setup is that any two cards in the deck have <i>exactly</i> one picture in common.
There are various sets of rules, but they all boil down to some variation of
"deal two cards, try to spot the common element."

To my surprise / delight, Madeline picked up the game very quickly and was quite good at it,
despite her not knowing any of the <i>Frozen</i> characters on account of having
never seen the movie. [That's right, I am Dad of the Year, hold your applause until the end.]

So I bought her her own set (<a href="http://www.amazon.com/Blue-Orange-00411-Spot-It/dp/B0039S7NO6/">original edition</a>)
and we started playing it at home.  The more I played it, the more I puzzled over its mathematics.
How would one go about designing such a deck?  

![spotit]({filename}images/spot_it.jpg)

I was unable to figure it out off the top of my head, so I Googled it.
Sure enough, I was not the first one to ask this question, although most of the
answers I found were not terrifically understandable.  I finally achieved enlightenment
through <a href="http://math.stackexchange.com/questions/36798/what-is-the-math-behind-the-game-spot-it/36806#36806">this StackExchange answer</a>
although it wasn't as clear as I liked.  Also, it didn't provide the code to generate the decks,
which I decided was a worthwhile exercise.  (As always, 
<a href="https://github.com/joelgrus/spot-it">the code is on GitHub</a>.)

The mathematics involves <a href="http://en.wikipedia.org/wiki/Projective_plane#Finite_projective_planes">finite projective planes</a>,
which I learned about so that I could explain them to you.

<h2>Projective Planes</h2>

In run-of-the-mill planes (the kind you likely studied in geometry class),
every two distinct points determine exactly one line.
And every two distinct lines intersect in either zero points (if they are parallel)
or one point (if they are not parallel).

A projective plane contains extra points at infinity where parallel lines can intersect.
This means that in a projective plane, any two distinct lines intersect in exactly one point.

One way to make this happen is to -- for each slope -- add a point at infinity
where all the lines of that slope intersect.  That is, add an "infinity 0"
where all horizontal lines intersect, an "infinity 1" where all lines with slope 1 intersect,
an "infinity infinity" where all the vertical lines intersect,
and so on.  Then, so that any two distinct points have exactly one line between them,
add a new "line at infinity" that goes through all the infinities.

<h2>Finite Projective Planes</h2>

Although you are probably not used to thinking about finite "planes", we can do something similar for them.

Choose some prime number n, 
and consider the n x n grid of points:

```python
def ordinary_points(n):
    return [(x, y) 
            for x in range(n) 
            for y in range(n)]
```

(We'll explain why we chose n to be prime in a bit.)

In this finite plane we do arithmetic <a href="http://en.wikipedia.org/wiki/Modular_arithmetic">mod n</a>, 
so that (for example) the set of points
with y = 0 is in fact a horizontal line that "wraps around" from (n - 1, 0) to (0, 0).

It turns out that there are n + 1 ordinary lines through (0, 0):

* slope 0: goes through (1, 0), (2, 0), ...
* slope 1: goes through (1, 1), (2, 2), ...
* slope 2: goes through (1, 2), (2, 4), ...
* slope 3: goes through (1, 3), (2, 6), ...
* ...
* infinite slope: goes through (0, 1), (0, 2), ...

and every point that's not (0, 0) lies on exactly one of these lines.

<blockquote>This is one place where the prime-ness of n matters.  For instance,
if we'd chosen n = 4, then the line with slope 0 

[(0, 0), (1, 0), (2, 0), (3, 0)]

and the line with slope 2

[(0, 0), (1, 2), (2, 0), (3, 2)]

both pass through (0, 0) and (2, 0), but clearly they're not the same line.  
n being prime ensures the "two points lie on exactly one line" condition.</blockquote>

Each ordinary (non-vertical) line is defined by its slope and its intercept.  For example, there is a line through (0, 0) with slope 1, 
which passes through (0, 0), (1, 1), (2, 2), and (3, 3).  And there is a line through (0, 1) with slope 1,
it passes through (0, 1), (1, 2), (2, 3), and (3, 0).  [Remember that we're doing arithmetic mod n.] Each vertical line is defined just by its x-coordinate.

Again we have the problem that parallel lines don't intersect, and again we'll solve it by 
adding "points at infinity", one for each slope.  We'll represent the "infinity" with slope 1
just as the number 1, and we'll represent the "vertical infinity" as the unicode `u"∞"`.

```python
def points_at_infinity(n):
    """infinite points are just the numbers 0 to n - 1
    (corresponding to the infinity where lines with that slope meet)
    and infinity infinity (where vertical lines meet)"""
    return range(n) + [u"∞"]
```

Now we just need to make sure the correct infinity belongs to each line:

```python
def ordinary_line(m, b, n):
    """returns the ordinary line through (0, b) with slope m
    in the finite projective plan of degree n
    includes 'infinity m'"""
    return [(x, (m * x + b) % n) for x in range(n)] + [m]
    
def vertical_line(x, n):
    """returns the vertical line with the specified x-coordinate
    in the finite projective plane of degree n
    includes 'infinity infinity'"""
    return [(x, y) for y in range(n)] + [u"∞"]
```

We also need to add another line that goes through the points at infinity:

```python
def line_at_infinity(n):
    """the line at infinity just contains the points at infinity"""
    return points_at_infinity(n)
```

<h2>Are You Sure About The "Two Lines One Point"?</h2>

I am.  But let's prove it.  Imagine we have two different lines.
We want to prove that they intersect in <i>exactly</i> one point.  
We have several types of lines, so we'll need to consider every possible combination of cases:

<b>two ordinary lines with the same slope:</b> 

Say we have the lines (m1, b1) and (m1, b2).  They intersect at an ordinary point if 
there is some x so that m1 * x + b1 = m1 * x + b2; that is, if b1 = b2.  
But since they're different lines, necessarily b1 doesn't equal b2.
So these lines just intersect at "infinity m1".

<b>two ordinary lines with different slope:</b> 

Say we have the lines (m1, b1) and (m2, b2). They clearly don't intersect at infinity,
since one passes through "infinity m1" and the other through "infinity m2".
They intersect at an ordinary point precisely if

m1 * x + b1 = m2 * x + b2 (mod n)

or if

(m1 - m2) * x = b2 - b1 (mod n)

Because <a href="http://en.wikipedia.org/wiki/Finite_field#Definitions.2C_first_examples.2C_and_basic_properties">n is prime</a>
(this is another place where the prime-ness is important), 
it turns out there is a unique x for which this is true, so that's where they intersect:

(x, (m1 * x + b1) mod n) = (x, (m2 * x + b2) mod n) 

<b>ordinary line (m1, b1), vertical line through x</b>.  

It's easy to see they intersect exactly at (x, m1 * x + b1)

<b>ordinary line (m1, b1), line at infinity</b>. 

Again, it's easy to see that they intersect exactly at "infinity m1".

<b>vertical line through x1, vertical line through x2</b>. 

Intersect exactly at "infinity infinity"

<b>vertical line through x, line at infinity</b>. 

Intersect exactly at "infinity infinity"

<h2>What the Hell?</h2>

This has a point, I promise.  Let's pick a n, say 7.  The corresponding projective plane
has 57 points (7x's * 7y's + another 8 at infinity) and 57 lines (8 slopes * 7 intercepts + line at infinity).
Each line passes through 8 of the points, and any two lines intersect in exactly one point.  Now mentally translate:

point <-> picture

line <-> card

passes through <-> contains

projective plane <-> deck

intersect in <-> have in common

Translated, the deck has 57 cards and 57 (distinct) pictures.  Each card contains 8 pictures,
and any two cards have in common exactly one picture.  That's exactly the game.
(Actually, for reasons unknown to the Internet, the version of the game you buy only has 55 cards.
But our version has 57 cards.)

How do we create a deck?  
First, let's create a couple of functions to collect all of the points and lines:

```python
def all_points(n):
    return ordinary_points(n) + points_at_infinity(n)

def all_lines(n):
    return ([ordinary_line(m, b, n) for m in range(n) for b in range(n)] +
            [vertical_line(x, n) for x in range(n)] +
            [line_at_infinity(n)])
```

This works, the only problem is the cards are not all that nice looking:

```python
In [x]: random.choice(all_lines(7))
Out[x]: [(0, 4), (1, 5), (2, 6), (3, 0), (4, 1), (5, 2), (6, 3), 1]

In [y]: random.choice(all_lines(7))
Out[y]: [(0, 5), (1, 5), (2, 5), (3, 5), (4, 5), (5, 5), (6, 5), 0]
```
Indeed, they have the "picture" `(1, 5)` in common.  We should probably
give the pictures nicer names.  The following function will use the names
you pass in:

```python
def make_deck(n, pics):
    points = all_points(n)

    # create a mapping from point to pic
    mapping = { point : pic 
                for point, pic in zip(points, pics) }

    # and return the remapped cards
    return [map(mapping.get, line) for line in all_lines(n)]
```

And now it's easy to play your own game of Spot It! in the shell:

```python
def play_game(deck):
    # make a copy so as not to muck with the original deck, then shuffle it
    deck = deck[:]
    random.shuffle(deck)

    # keep playing until fewer than 2 cards are left    
    while len(deck) >= 2:
        card1 = deck.pop()
        card2 = deck.pop()
        random.shuffle(card1)  # shuffle the cards, too, to simulate that
        random.shuffle(card2)  # they might face different directions

        # find the matching element
        match, = [pic for pic in card1 if pic in card2]  

        print card1
        print card2
        
        guess = raw_input("Match? ")
        if guess == match:
            print "correct!"
        else:
            print "incorrect!"
```

For example, if I give it animal names, a play of the game looks like:

```python
In [x]: play_game(deck)
['Crab', 'Baboon', 'Rat', 'Jackal', 'Bear', 'Buffalo', 'Llama', 'Sheep']
['Snake', 'Yak', 'Jackal', 'Otter', 'Kouprey', 'Wolf', 'Rook', 'Ox']
Match? Jackal
correct!
['Narwhal', 'Coyote', 'Dog', 'Wolf', 'Dotterel', 'Rat', 'Mosquito', 'Tarsier']
['Gnu', 'Dogfish', 'Sheep', 'Porcupine', 'Mosquito', 'Heron', 'Tapir', 'Rook']
Match? Narwhal
incorrect!
```

and so on.  And now you know how the game works.  Maybe next time we'll 
<a href="https://github.com/joelgrus/spot-it/blob/master/haskell/SpotIt.hs">do it in Haskell</a>!