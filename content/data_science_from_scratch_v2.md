Title: Data Science From Scratch: Second Edition
Date: 2019-05-13 12:00
Category: Life, Data Science, Writing

I am thrilled to announce that the second edition of <i>Data Science from Scratch</i> is now available! (buy from <a href = "https://www.amazon.com/Data-Science-Scratch-Principles-Python/dp/1492041130">Amazon</a> or your other favorite bookstore, or read on Safari).

It's been almost exactly four years since the first edition came out,
and over that time it's helped dozens of people learn data science, Python, or possibly some combination of the two.

However, the first edition used Python 2.7. And as time ticks by,
I've been feeling guiltier and guiltier about having a book out there
with my name on it that tells people to use Python 2. Because in [current year],
<a href = "https://twitter.com/AutomationPanda/status/1125401079729008645">you should not be using Python 2</a>. Stop using Python 2!

![python 2 rip]({static}images/python2.jpg)

Eventually I realized that the only way to clear my conscience
was to prepare a second edition that advocated for Python 3. Accordingly,
the new edition is based on fresh, clean Python 3.6.
(Except for a standalone section on <a href = "https://docs.python.org/3/library/dataclasses.html">dataclasses</a>,
 which is based on Python 3.7, for obvious reasons.)

But since I was already in there fixing things,
I decided to _really_ fix things:

* I cleaned up all the code. I'm a much better coder than I was 4 years ago,
  and so I spent a lot of time making the examples and implementations
  cleaner and more readable. (I also removed language features like
  `map` and `filter` and `partial` that I've since decided are best avoided.
  Feel free to argue with me about this on Twitter, everyone else seems to.)
* I added an emphasis on using `assert` statements to test your code,
  which I wove throughout the book's narrative. I also used a lot more
  `assert` statements that didn't appear in the book but that helped me
  be more confident that the code is correct.
* I used Python-3.6-style <a href = "https://docs.python.org/3/library/typing.html">type annotations</a> for most
  of the code in the book. This may strike you as objectionable,
  as a lot of people don't like type hints in Python. Nonetheless,
  I decided it was the right choice both morally and pedagogically,
  so bear with me,
  and by the end of the book you'll wonder how you ever lived without them.
  I also used these to help ensure that the code in the book is correct.
* I fixed all the examples that were broken.
  For example, <a href="https://www.oreilly.com/ideas/the-mission-of-spreading-the-knowledge-of-innovators-continues">the O'Reilly store no longer exists</a>,
  which means that the "scraping the O'Reilly store" example
  no longer works. I replaced it with an example that involved
  scraping `congress.gov`. (Will that site exist in 4 years? Who knows?)
  I also fixed the Twitter authentication instructions, although there's
  a good chance they're broken again by now.
* I made many of the examples better. I replaced the janky 8x8 homemade
  digits in the neural networks chapter with the MNIST dataset. And so on.
* I convinced them to replace all the bit.ly links with the original URLs
  (you're welcome).
* I added a new chapter on "Deep Learning". Admit it, you want to learn about
  deep learning! Over the last couple of years I've been doing a
  <a href = "https://joelgrus.com/2017/12/04/livecoding-madness-building-a-deep-learning-library/">livecoding stunt</a> that involves building a deep learning
  library from scratch in an hour. I adopted that approach into a new chapter
  (which took a lot more than an hour to write).
* I built on the "deep learning" code to modernize the NLP chapter,
  adding new sections on word2vec and RNNs.
* Finally, I added a "Data Ethics" chapter, assuming that
  by the time people get to the end of the book they probably
  want to know what I think about data ethics.

All that said, on some level it is just
an *improved, more-modern version of the first edition*.
If you are a Joel Grus completist (or if you haven't read the first edition)
(or if you need a kick in the pants to upgrade to Python 3)
(or if you want to learn about type annotations)
then you probably want to read it. If you already read the first edition
then maybe you'll be happy just poking at
the <a href = "https://github.com/joelgrus/data-science-from-scratch">new code on GitHub</a>.

Also, the cover looks extremely different, as O'Reilly has completely changed
their design language. So if you are an O'Reilly cover completist
you might also want to get it.

![book cover]({static}images/dsfs_v2.jpg)

Anyway, I am extremely thrilled to share the new edition with you
and (in particular) to no longer have a Python 2 book out there
with my name on it. (I mean, the first edition is still *out there*,
and I'm sure I'll still be fielding errata about it until the sun burns out,
but at least now it's officially defunct.)

Enjoy!
