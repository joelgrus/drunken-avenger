Title: Constructive Mathematics in F# (and Clojure)
Date: 2013-08-26 06:23
Author: joelgrus
Tags: Hacking, Mathematics, Technology
Slug: constructive-mathematics-in-f-and-clojure

(Tell me what a terrible person I am on [Hacker
News](https://news.ycombinator.com/item?id=6276848).)

For as long as I can remember^[1](#footnote)^ I've dreamed of
reimplementing the entirety of mathematics from scratch. And now that
I've finished the "Wheel of Time" series I have a little bit of extra
time on my hands each day, which has allowed me to take baby steps
toward my dream.

**What this is**

An implementation of mathematics in F\# (and also in Clojure)

**What this is not**

An *efficient* implementation of mathematics in F\# (or in Clojure)

You would never want to use this library to *do* mathematics, as it is
chock-full of all sorts of non-tail-recursive function calls that will
blow your stack like there's no tomorrow. (If you don't know what that
means, just take my word that you would never want to use this library
to *do* mathematics.) Instead, this library is an interesting way to
learn about

-   how to construct a mathematics from scratch
-   how to implement a mathematics in F\# (or Clojure)
-   my bizarre obsessions

As always when I work on stuff like this, the code is on my
[GitHub](https://github.com/joelgrus).

-   [F\#
    code](https://github.com/joelgrus/constructive-mathematics-fsharp)
-   [Clojure
    code](https://github.com/joelgrus/constructive-mathematics-clojure)

This was originally just going to be in F\#, and then I read a couple of
blog posts about ClojureScript, which reminded me I'd been meaning to do
something in Clojure, so why not implement the same stuff a second time?
(This is why "in Clojure" is in parentheses everywhere, and why the F\#
code has all the comments.) I tried to make the F\# code F\#-y and the
Clojure code Clojure-y, but I'm not sure how well I succeeded.

I won't go into excruciating detail about either mathematical theory or
F\# (or Clojure), but hopefully you can understand both from the detail
I do go into. I also will only call a few high points of each codebase,
if you want more gory details check out GitHub.

Both sets of code have handfuls of tests written, which should give you
a good sense of how both libraries operate.

Comparisons
-----------

In F\#, I'll define a discriminated union

    type Comparison = LessThan | Equal | GreaterThan

In Clojure you don't typically use "types", but we can just use keywords
`:less-than` and `:equal` and `:greater-than`.

Natural Numbers
---------------

We'll define these recursively. A natural number is either

-   "One" (which is just some thing, forget that you're already familiar
    with a "one"), or
-   the "Successor" of a different natural number

Anything you can make using these rules is a natural number. Anything
that you can't isn't.

We'll call the successor of One "Two", and the successor of Two "Three",
keeping in mind that at this point those are just names attached to
things without any meaning other than "Two is the successor of One" and
"Three is the successor of Two".

In F\# we can do this with a discriminated union:

    type Natural = One | SuccessorOf of Natural
    let Two = SuccessorOf One
    // and so on

After trying a lot of things in Clojure, I finally decided the most
~~Clojure-ish~~ Clojurian way was

    (defn successor-of [n] {:predecessor n})
    (def one (successor-of nil))
    (def two (successor-of one))
    ; and so on

Although the Clojure way at first looks backward, if you think about it
both ways define the "successor of One" to be the number whose
"predecessor" is One.

Next we'll want to use this recursive structure to create an arithmetic.
For instance, we can easily *add* two natural numbers:

    let rec Add (n1 : Natural) (n2 : Natural) =
        match n1 with
            // adding One to a number is the same as taking its Successor
        | One -> SuccessorOf n2
            // otherwise n1 has a predecessor, add it to the successor of n2
            // idea: n1 + n2 = (n1 - 1) + (n2 + 1)
        | SuccessorOf n1' -> Add n1' (SuccessorOf n2)

</code>

Clojure doesn't have built-in pattern-matching, so instead I did
something similar using a `one?` function:

    (defn add [n1 n2]
      (if (one? n1)
        (successor-of n2)
        (add (predecessor-of n1) (successor-of n2))))

Both make it easy to create lazy infinite sequences of all natural
numbers.

    let AllNaturals = Seq.unfold (fun c -> Some (c, SuccessorOf c)) One

</code>

and

    (def all-naturals (iterate successor-of one))

And (blame it on the natural numbers) both run into trouble when you try
to define *subtraction*. In F\# the natural thing to do is return an
[Option type](http://msdn.microsoft.com/en-us/library/dd233245.aspx):

    // now, we'd like to define some notion of subtraction as the inverse of addition
    // so if n1 + n2 = n3, then you'd like "n3 - n2" = n1
    // but this isn't always defined, for instance 
    //  n = One - One
    // would mean One = One + n = SuccessorOf n, which plainly can never happen
    // in this case we'll return None
    let rec TrySubtract (n1 : Natural) (n2 : Natural) =
        match n1, n2 with
            // Since n1' + One = SucessorOf n1', then SuccessorOf n1' - One = n1'
        | SuccessorOf n1', One -> Some n1'
            // if n = (n1 + 1) - (n2 + 1), then
            //    n + n2 + 1 = n1 + 1
            // so n + n2 = n1,
            // or n = n1 - n2
        | SuccessorOf n1', SuccessorOf n2' -> TrySubtract n1' n2'
        | One, _ -> None // "Impossible subtraction"

In Clojure there is no option type, so I just returned `nil` for a bad
subtraction:

    (defn try-subtract [n1 n2]
      (cond
        (one? n1) nil
        (one? n2) (predecessor-of n1)
        :else (try-subtract (predecessor-of n1) (predecessor-of n2))))

Integers
--------

The failure of "subtraction" leads us to introduce the Integers, which
you can (if you are so inclined) think of as *equivalence classes of
pairs of natural numbers*, where (for instance),

    (Three,Two) = (Two,One) = "the result of subtracting one from two" = 
     "the integer corresponding to one"

In F\# we can again define a custom type:

    type Integer =
    | Positive of Natural.Natural
    | Zero
    | Negative of Natural.Natural

and map to equivalence classes using

    let MakeInteger (plus,minus) =
        match Natural.Compare plus minus with
        | Comparison.Equal -> Zero
        | Comparison.GreaterThan -> Positive (Natural.Subtract plus minus)
        | Comparison.LessThan -> Negative (Natural.Subtract minus plus)

whereas in Clojure we just use maps:

    (def zero {:sign :zero})
    (defn positive [n] {:sign :positive, :n n})
    (defn negative [n] {:sign :negative, :n n})

and the very similar

    (defn make-integer [plus minus]
      (let [compare (natural-numbers/compare plus minus)]
        (case compare
          :equal zero
          :greater-than (positive (natural-numbers/subtract plus minus))
          :less-than (negative (natural-numbers/subtract minus plus)))))

We can easily define addition and subtraction and even multiplication,
but when we get to division we run into problems again. You'd like 1 / 3
to be the number that when multiplied by three yields one. But there is
no such Integer.

    let rec TryDivide (i1 : Integer) (i2 : Integer) =
        match i1, i2 with
        | _, Zero -> failwithf "Division by Zero is not allowed"
        | _, Negative _ -> TryDivide (Negate i1) (Negate i2)
        | Zero, Positive _ -> Some Zero
        | Negative _, Positive _ -> 
            match TryDivide (Negate i1) i2 with
            | Some i -> Some (Negate i)
            | None -> None
        | Positive _ , Positive _ ->
            if LessThan i1 i2
            then None // cannot divide a smaller integer by a larger one
            else 
                match TryDivide (Subtract i1 i2) i2 with
                | Some i -> Some (SuccessorOf i)
                | None -> None

and similarly

    (defn try-divide [i1 i2] =
      (cond
         (zero? i2) (throw (Exception. "division by zero is not allowed"))
         (negative? i2) (try-divide (negate i1) (negate i2))
         (zero? i1) zero
         (negative? i1) (let [td (try-divide (negate i1) i2)]
                               (if td (negate td)))
         :else ; both positive
           (if (less-than i1 i2)
             nil
             (let [td (try-divide (subtract i1 i2) i2)]
               (if td (successor-of td))))))

</code>

And if we're clever we can get a lazy sequence of all prime numbers:

    let rec IsPrime (i : Integer) =
        match i with
        | Zero -> false
        | Negative _ -> IsPrime (Negate i)
        | Positive Natural.One -> false
        | Positive _ ->
            let isComposite =
                Range Two (AlmostSquareRoot i)
                |> Seq.exists (fun i' -> IsDivisibleBy i i')
            not isComposite 

    let AllPrimes =
        Natural.AllNaturals
        |> Seq.map Positive
        |> Seq.filter IsPrime

</code>

and in Clojure

    (defn prime? [i]
      (cond
        (zero? i) false
        (negative? i) (prime? (negate i))
        (equal-to i one) false
        :else (not-any? #(is-divisible-by i %) (range two (almost-square-root i)))))

    (def all-primes
      (->> natural-numbers/all-naturals
        (map positive)
        (filter prime?)))

</code>

Rational Numbers
----------------

Now, to solve the "division problem", we can similarly look at
equivalence classes of pairs of *integers*, just as long as the second
one isn't zero.

    // motivated by the "division problem" -- given integers i1 and i2, where i2 not zero,
    // would like to define some number q = Divide i1 i2, such that EqualTo i1 (Multiply q i2) 

    // proceeding as above, why not define a new type of number as a *pair* (i1,i2) representing
    // the "quotient" of i1 and i2.  Again such a representation is not unique, as you'd want
    // (Two,One) = (Four,Two) = [the number corresponding to Two]

    // when do we want (i1,i2) = (i1',i2') ?  
    // when there is some i3 with i1 = i2 * i3, i1' = i2' * i3, or
    // precisely when we have i1 * i2' = i1' * i2

    // in particular, if x divides both i1 and i2, so that i1 = i1' * x, i2 = i2' * x, then
    // i1 * i2' = i1' * x * i2' = i1' * i2, so that (i1, i2) = (i1', i2')

    type Rational(numerator : Integer.Integer, denominator : Integer.Integer) =
        let gcd = 
            if Integer.EqualTo Integer.Zero denominator then failwithf "Cannot have a Zero denominator"
            else Integer.GCD numerator denominator
            
        // want denominator to be positive always
        let reSign =
            match denominator with
            | Integer.Negative _ -> Integer.Negate
            | _ -> id

        // divide by GCD to get to relatively prime
        let _numerator = (Integer.Divide (reSign numerator) gcd)
        let _denominator = (Integer.Divide (reSign denominator) gcd)

        member this.numerator with get () = _numerator
        member this.denominator with get () = _denominator

or

    (defn rational [numerator denominator]
          (let [gcd (if (integers/equal-to integers/zero denominator)
                      (throw (Exception. "cannot have a zero denominator!"))
                      (integers/gcd numerator denominator))
                re-sign (if (integers/less-than denominator integers/zero)
                          integers/negate
                          (fn [i] i))]
            {:numerator (integers/divide (re-sign numerator) gcd),
             :denominator (integers/divide (re-sign denominator) gcd)}))

There is lots of extra code around the rationals, although it's hard to
run into limitations as we did before. The most common limitation is
that there's no rational whose square is two, but it's hard to run into
that limitation without [reasoning outside the
system](http://en.wikipedia.org/wiki/Square_root_of_2#Proofs_of_irrationality).

Real Numbers
------------

Two common ways of constructing the real numbers from the rationals are
[Dedekind
Cuts](http://en.wikipedia.org/wiki/Construction_of_the_real_numbers#Construction_by_Dedekind_cuts)
and equivalence classes of [Cauchy
Sequences](http://en.wikipedia.org/wiki/Construction_of_the_real_numbers#Construction_from_Cauchy_sequences).
Neither is easy to implement in code.

Instead, I found a way to specify real numbers as [cauchy sequences
*along with* specific cauchy
bounds](http://en.wikipedia.org/wiki/Constructivism_(mathematics)#Example_from_real_analysis):

    // following http://en.wikipedia.org/wiki/Constructivism_(mathematics)#Example_from_real_analysis
    // we'll define a Real numbers as a pair of functions:
    // f : Integer -> Rational
    // g : Integer -> Integer
    // such that for any n, and for any i and j >= g(n) we have
    //  AbsoluteValue (Subtract (f i) (f j)) <= Invert n

    type IntegerToRational = Integer.Integer -> Rational.Rational
    type IntegerToInteger = Integer.Integer -> Integer.Integer
    type Real = IntegerToRational * IntegerToInteger

    let Constantly (q : Rational.Rational) (_ : Integer.Integer) = q
    let AlwaysOne (_ : Integer.Integer) = Integer.One
    let FromRational (q : Rational.Rational) : Real = (Constantly q), AlwaysOne

or

    (defn real [f g] {:f f, :g g})
    (defn f-g [r] [(:f r) (:g r)])

    (defn constantly [q] (fn [_] q))
    (defn always-integer-one [_] integers/one)

    (defn from-rational [q] (real (constantly q) always-integer-one))

One interesting twist here is that it is impossible to say whether two
numbers are equal without reasoning outside the system. For instance,
the real number `FromRational Rational.Zero` is equal to the real number

    (Rational.FromInteger >> Rational.Invert, Rational.FromInteger >> Rational.Invert)

(which represents the sequence 1, 1/2 , 1/3, 1/4, ...), but again you
can only reason about that outside of code. Instead you can define
`CompareWithTolerance` which -- given a *tolerance* -- can tell you that
one number is definitively greater than another, or that they're
"approximately equal".

The ultimate test here would be to show that the real number

    let SquareRootOfTwo : Real =
        let rationalTwo = Rational.FromInteger Integer.Two
        let sq x = Rational.Subtract (Rational.Multiply x x) rationalTwo
        let sq' x = Rational.Multiply x rationalTwo
        // newton's method
        let iterate _ guess = Rational.Subtract guess (Rational.Divide (sq guess) (sq' guess))
        let f = memoize iterate Rational.One
        let g (n : Integer.Integer) = n
        f, g

gives you the real number `FromRational Rational.Two` when you square
it. It looks like it should. Unfortunately, trying to do so will blow up
the call stack, so it's not advised. Maybe someday I'll go back and try
to make everything
[tail-recursive](http://en.wikipedia.org/wiki/Tail_call).

Gaussian Integers
-----------------

Another drawback of the Integers is that none of them have negative
squares. One way to solve this is by adding a number "i" whose square is
negative one. I got kind of bored with these, so I never took them too
far and never wrote any tests.

Complex Numbers
---------------

The obvious next step would be to add the square root of negative one
"i" to the real numbers. But since they're not working so great I never
did this.

Conclusion
----------

I spent way too much time on this project, and I really need to get back
to other things, like the group-couponing site I'm planning to build, so
I'm ready to call this quits. Here are some things I learned:

1\. Math is hard.\
 2. Writing the Clojure versions was more "fun". However,\
 3. Getting the F\# versions to work was much easier, because most of my
Clojure bugs would have been caught by a type checker (or were caused by
using maps as types and then having them unintentionally decompose).\
 4. If I put this much work into *useful* ideas, imagine what I could
accomplish!\
 5. Probably I shouldn't read "Wheel of Time" again.

<a name="footnote"></a><small>1. Which is approximately 1 week.</small>
