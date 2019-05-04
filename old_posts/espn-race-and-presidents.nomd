Title: ESPN, Race, and Presidents
Date: 2013-05-23 06:40
Author: joelgrus
Tags: Data, Hacking
Slug: espn-race-and-presidents

Inspired by (and lifting large amounts of code from) Trey Causey's
[investigation of the language that ESPN uses to discuss white and
non-white quarterbacks](http://thespread.us/blog/?p=39), I similarly
wondered about the language ESPN uses to discuss white and non-white
*Presidents*. For instance, a common stereotype is that non-white
Presidents assassinate their citizens using unmanned drones, while white
Presidents assassinate their citizens using polonium-210. Do such
stereotypes creep into sportswriting?

Toward that end, I used [Scrapy](http://www.scrapy.org/) to scrape all
the articles from the ESPN website that matched searches for (president
obama), (president bush), (president clinton), and so on. This gave me a
total of 543 articles. Then, using
[Wikipedia](https://en.wikipedia.org/wiki/Black_president#Presidents_and_presidential_candidates),
[Mechanical Turk](https://requester.mturk.com/tour/categorization), and
a proprietary [deep
learning](http://en.wikipedia.org/wiki/Deep_learning) model, I
categorized each of these Presidents as either "white" or "non-white".

Using [NLTK](http://nltk.org/), I tokenized each article into sentences
and then identified each sentence as being about

-   one or more white Presidents
-   one or more non-white Presidents
-   both white and non-white Presidents
-   no presidents

Curiously, while there were very few "non-white" Presidents, there were
nonetheless about *four times as many* "non-white" sentences as "white"
sentences. (This is itself an interesting phenomenon that's probably
worth investigating.)

I then split each sentence into words and counted how many times each
word appeared in "white", "non-white", "both", and "none" sentences.
Like Trey, I followed the analysis
[here](http://nbviewer.ipython.org/5105037), similarly excluding
stopwords and proper nouns, which I inferred based on capitalization
patterns.

Finally, for each word I computed a "white percentage" and "non-white
percentage" by looking at how likely that word was to appear in a
"white" sentence or a "non-white" sentence and adjusting for the
different numbers of sentences.

After all that, here are the words that were most likely to appear in
sentences about "white" Presidents:

plaque 5\
 severed 4\
 grab 4\
 investigation 3\
 worn 3\
 unable 3\
 child 3\
 suppose 3\
 block 3\
 living 3\
 holders 3\
 pounds 3\
 ticket 3\
 blackout 3\
 thrown 3\
 exercise 3\
 scene 3\
 televised 3\
 upon 3\
 executives 3

Clearly this reads like something out of "CSI" or possibly "CSI: Miami".
If I were to make these words into a story, it would probably be
something macabre like

> The President **grabbed** the **plaque** he'd secretly made from a
> **living** **child**'s **severed** foot and **worn** sock. The
> **investigation** **supposed** a suspect weighing at least 200
> **pounds** who could have **thrown** the victim down the **block**,
> not a feeble politician famous for his **televised** **blackout** when
> he tried to **exercise** but was **unable** to **grab** his toes.

In constrast, here are the words most likely to appear in sentences
about "non-white" Presidents:

bracket 32\
 interview 21\
 trip 16\
 champions 16\
 fan 48 1\
 asked 35 1\
 carrier 11\
 celebrate 11\
 thinks 11\
 early 11\
 eight 11\
 personal 10\
 picks 10\
 appearance 10\
 far 9\
 hear 9\
 congratulating 9\
 given 9\
 troops 9\
 safety 9\
 fine 9\
 person 9

This story would have to be something uplifting like

> The President promised to raise taxes on every **bracket** before
> ending the **interview**. As a huge water polo **fan**, he needed to
> catch a ride on an aircraft **carrier** for his **trip** to
> **celebrate** with the **champions**. "Sometimes I get **asked**," he
> **thinks**, "whether it's too **early** to eat a **personal** pan
> pizza with **eight** toppings. So **far** I always say that I **hear**
> it's not." His **safety** is a **given**, since he's surrounded by
> **troops** who are always **congratulating** him for being a **fine**
> **person** with a **fine** **appearance**.

As you can see, it has a markedly different tone, but not in a way that
obviously correlates with the stereotypes mentioned earlier. Whatever
prejudices lurk at ESPN are exceedingly subtle.

Obviously, this is only the tip of the iceberg. The algorithm for
identifying which sentences were about Presidents is pretty rudimentary,
and the word-counting NLP techniques used here are pretty basic. Another
obvious next step would be to pull in additional data sources like
[Yahoo! Sports](http://sports.yahoo.com/) or
[SI.com](http://sportsillustrated.cnn.com/) or [FOX
Sports](http://msn.foxsports.com/).

If you're interested in following up, the code is all up on my
[github](https://github.com/joelgrus/presidents), so have at it! And I'd
love to hear your feedback.
