Title: Great Ethicists, Webcomics, Game Theory, and the Iterated Prisoner's Dilemma
Date: 2010-06-05 18:26
Author: joelgrus
Tags: Economics, Philosophy
Slug: great-ethicists-webcomics-game-theory-and-the-iterated-prisoners-dilemma

The webcomic [Saturday Morning Breakfast
Cereal](http://www.smbc-comics.com/index.php?db=comics&id=1899#comic)
today covers one of my favorite topics: Game Theory and the Social
Contract.

The game theory, unfortunately, is not done very carefully. Here's the
Prisoner's Dilemma setup:

  ----------------------- ----------------------- -----------------------
                          RAT OUT                 REMAIN SILENT

  RAT OUT                 Both get 1 year in      1 goes free, 2 gets 5
                          prison                  years

  REMAIN SILENT           2 goes free, 1 gets 5   Both get 6 months
                          years                   
  ----------------------- ----------------------- -----------------------

In this table, player 1 chooses the row and player 2 chooses the column.
If both REMAIN SILENT, both get 6 months in prison. If each RATS OUT the
other, both get 1 year in prison. And if one RATS OUT and the other
REMAINS SILENT, the rat goes free and the mute gets 5 years in prison.

Here's how the comic summarizes things:

> So, even though [the bottom right corner] is the best choice, the
> perfectly rational people pick [the top left corner].

Now, the bottom right corner is emphatically *not* the "best choice."
For starters, given our setup, we're not choosing a corner. One person
chooses a row, and (completely separately) one person chooses a column.
There's no way to *choose* a corner, and therefore there's no "best
choice" of corner.

But let's ignore this nitpick and assume he said "best *outcome*." Even
this isn't true. Player 1 would be better off with the top right corner,
and player 2 would be better with the bottom left corner. This would
seem to disqualify the bottom right corner as being "best." What he
probably meant to say is that it's *better* than the top left corner,
which happens to be the "rational" (i.e. dominant strategy equilibrium)
outcome.

In fact, this is the *point* of the prisoner's dilemma: no matter what
the other player does, your best choice is to RAT OUT, and so the
outcome when "rational" people play is the top left corner. Which is
worse for both players than if they'd both REMAINED SILENT. Hence the
dilemma. "Everyone act rational" doesn't always lead to optimal
outcomes.

The comic then tries to apply this model to morality. The "great
ethicists of history," it turns out, have been trying to convince people
to pick [sic] the bottom right corner. (As mentioned above, we'll assume
that the comic really means that they're trying to convince people to
pick STAY SILENT.) The utilitarian Bentham is pictured trying to
convince people that the bottom right corner is utilitarianly awesome.
And the damnitarian Jesus is pictured trying to convince people that the
top left corner will land you in hell for eternity.

In short, each is trying to artificially change the payoffs of the game.
Bentham is trying to convince you to that you should care about the
[total time spent in prison by both
players](http://en.wikipedia.org/wiki/Jeremy_Bentham#Utilitarianism),
not just the time spent by you. It's easy to see why this is an uphill
battle. (Furthermore, all this does is turn the game into a [pure
coordination
game](http://en.wikipedia.org/wiki/Coordination_game#Examples) with
[three different
equilibria](http://en.wikipedia.org/wiki/Coordination_game#Mixed_Nash_equilibrium),
one of which is still [RAT OUT, RAT OUT]. Smooth move, Bentham!)

Jesus, on the other hand, is (according to the comic) trying to convince
you that the payoff in the top left corner is actually more like
*infinitely many* years in prison. Since game theory doesn't do well
with infinite payoffs, this actually results in a game with no
equilibrium, which seems like kind of a dick-ish thing to do. However,
it seems weird to condemn someone only if *both* he and his opponent RAT
OUT. A more reasonable Lord-of-the-Universe thing to do would be to give
you hugely-negative payoff whenever you RAT OUT, regardless of what your
opponent does. And in that case it's a [dominant-strategy
equilibrium](http://en.wikipedia.org/wiki/Strategic_dominance#Dominance_and_Nash_equilibria)
to keep your mouth shut. (Unfortunately, Jesus ruined his "ethicist"
credibility by insisting that the same infinite punishments also apply
to people who commit the prisoner's-dilemma-unrelated "crime" of not
accepting him as their personal savior.)

Independent of our ethicists, the game we've described is not a
particularly compelling model of morality. Life contains plenty of
"cooperate or defect" situations, sure, but for the most part these
situations occur repeatedly with the same cast of characters. Imagine
that you and I play the above-described game day after day after day.
(You'll probably have to change the payoffs to involve money or pain or
something, since playing a "go to prison for a year" game every day
doesn't make a whole lot of sense. Just make sure to keep the same
strategic structure and relative payoffs.)

It turns out (thanks, Robert Aumann) that when you [repeat the
prisoner's
dilemma](http://en.wikipedia.org/wiki/Repeated_game#Repeated_prisoner.27s_dilemma)
indefinitely, suddenly ratting out isn't so rational. Imagine that I'm
willing to KEEP SILENT for as long as you do, but if you ever RAT OUT
then I'll start RATTING OUT for the rest of time. It's not hard to see
that if you adopt the same strategy, we can land in the bottom right
corner over and over and over again, because the one-time payoff from
defecting would be vastly outweighed by the ensuing sequence of top-left
outcomes. As long as we're describing repeated interactions, there's not
a lot of a problem.

Another criticism of this line of modeling is that many situations where
we'd normally think to apply "morality" are *unilateral* ones, not
*strategic* ones. "Thou shalt not kill," "thou shalt not steal," and
similar rules are all
[decision-theoretic](http://en.wikipedia.org/wiki/Decision_theory)
prescriptions, not game-theoretic ones. The Prisoner's Dilemma (and game
theory more generally) describes situations where the outcome to me
depends both on my decisions and on yours. But (for example) my decision
whether to steal from you is not typically co-mingled with your
simultaneous decision whether to steal from me. My decision whether to
steal from you probably has more to do with the (implicit or explicit)
"social contract" that society has in place.

(Of course you could construct a Prisoner's-Dilemma-flavored model in
which every day you and I decide whether to rob each other, but you'd
have a hard time convincing me that your model was in any way a
representation of the actual choices and incentives that each of us
faces in today's world.)

In fact, there are some pretty interesting [game theoretic
considerations](http://www.amazon.com/gp/product/0195178114?ie=UTF8&tag=brightwalton-20&linkCode=as2&camp=1789&creative=390957&creativeASIN=0195178114)![](http://www.assoc-amazon.com/e/ir?t=brightwalton-20&l=as2&o=1&a=0195178114)
that come into play when we think about the (theoretical) adoption of
such a social contract, which involves strategy all around. But that's
probably a little much to fit into a webcomic.
