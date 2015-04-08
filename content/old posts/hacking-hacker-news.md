Title: Hacking Hacker News
Date: 2012-02-16 18:07
Author: joelgrus
Tags: Data, Hacking, Science
Slug: hacking-hacker-news

[Hacker News](http://news.ycombinator.com/), if you don't know it, is an
aggregator / forum attached to [Y Combinator](http://ycombinator.com/).
People submit links to news stories and blog posts, questions, examples,
and so on. Other people vote them up or down, and still other people
argue about them in the comments sections.

![](http://joelgrus.com/wp-content/uploads/2012/02/hn.png "hn")

If you have unlimited time on your hands, it's an excellent firehose for
things related to hacking. If your time is more limited, it's more
challenging. People submit hundreds of stories every day, and even if
you only pay attention to the ones that get enough votes to make it to
the homepage, it's still overwhelming to keep up:

![](http://joelgrus.com/wp-content/uploads/2012/02/hackernewsunread.png "hackernewsunread")

What's more, a lot of the stories are about topics that are boring, like
OSX and iPads and group couponing. So for some time I've been thinking
that what Hacker News really needs is some sort of filter for "only show
me stories that Joel would find interesting". Unfortunately, it has no
such filter. So last weekend I decided I would try to build one.

**Step 1 : Design**

To make things simple, I made a couple of simplifying design decisions.

First, I was only going to take into account *static* features of the
stories. That meant I could consider their title, and their url, and who
submitted them, but not how many comments they had or how many votes
they had, since those would depend on when they were scraped.

In some ways this was a severe limitation, since HN itself uses the
votes to decide which stories to show people. On the other hand, the
whole point of the project was that "what Joel likes" and "what the HN
community likes" are completely different things.

Second, I decided that I wasn't going to *follow* the links to collect
data. This would make the data collection easier, but the predicting
harder, since the titles aren't always indicative of what's behind them.

So basically I would use the story *title*, the *URL* it linked to, and
the submitter's *username*. My goal was just to classify the story as
*interesting-to-Joel* or not, which meant the simplest approach was
probably to use a [naive Bayes
classifier](http://en.wikipedia.org/wiki/Naive_Bayes_classifier), so
that's what I did.

**Step 2 : Acquire Computing Resources**

I have an AWS account, but for various reasons I find it kind of
irritating. I'd heard some good things about [Rackspace Cloud
Hosting](http://www.rackspace.com/cloud/), so I signed up and launched
one of their low-end \$10/month virtual servers with (for no particular
reason) Debian 6.0.

I also installed a recent Ruby (which is these days my preferred
language for building things quickly) and
[mongoDB](http://www.mongodb.org/), which I'd been meaning to learn for
a while.

**Step 3 : Collect Data**

First I needed some history. A site called [Hacker News
Daily](http://www.daemonology.net/hn-daily/) archives the top 10 stories
each day going back a couple of years, and it was pretty simple to write
a script to download them all and stick them in the database.

Then I needed to collect the new stories going forward. At first I tried
scraping them off the Hacker News
["newest"](http://news.ycombinator.com/newest) page, but very quickly
they blocked my scraping (which I didn't think was particularly
excessive). Googling this problem, I found the [unofficial Hacker News
API](http://api.ihackernews.com/), which is totally cool with me
scraping it, which I do once an hour. (Unfortunately, it seems to go
down several times a day, but what can you do?)

**Step 4 : Judging Stories**

Now I've got an ever-growing database of stories. To build a model that
classifies them, I need some training data with stories that are labeled
*interesting-to-Joel* or not. So I wrote a script that pulls all the
unlabeled stories from the database, one-at-a-time shows them to me and
asks whether I'd like to click on the story or not, and then saves that
judgment back to the database.

![](http://joelgrus.com/wp-content/uploads/2012/02/judger.png "judger")

At first I was judging them *most-recent-first*, but then I realized I
was biasing my traning set toward SOPA and PIPA, and so I changed it to
judge them randomly.

**Step 5 : Turning Stories into Features**

The naive Bayes model constructs probabilities based on *features* of
the stories. This means we need to turn stories into features. I didn't
spend too much time on this, but I included the following features:

\* contains\_{word}\
 \* contains\_{bigram}\
 \* domain\_{domain of url}\
 \* user\_{username}\
 \* domain\_contains\_user (a crude measure of someone submitting his
own site)\
 \* is\_pdf (generally I don't want to click on these links)\
 \* is\_question\
 \* title\_has\_dollar\_amount\
 \* title\_has\_number\_of\_years\
 \* title\_references\_specific\_YC\_class (e.g. "(YC W12) seeks blah
blah)\
 \* title\_is\_in\_quotes

For the words and bigrams, I removed a short list of stopwords, and I
ran them all through a [Porter
stemmer](http://en.wikipedia.org/wiki/Stemming). The others are all
pretty self-explanatory.

**Step 6 : Training a Model**

This part is surprisingly simple:

\* Get all the judged stories from the database.\
 \* Split them into a training set and a test set. (I'm using an 80/20
split.)\
 \* Compute all the features of the stories in the training set, and for
each feature count (\# of occurrences in liked stories) and (\# of
occurrences in disliked stories).\
 \* Throw out all features that don't occur at least 3 times in the
dataset.\
 \* [Smooth](http://en.wikipedia.org/wiki/Additive_smoothing) each
remaining feature by adding an extra 2 likes and an extra 2 dislikes. (2
is on the large side for smoothing, but we have a pretty small
dataset.)\
 \* That's it. We [YAML](http://en.wikipedia.org/wiki/YAML)-ize the
feature counts and save them to a file.\
 \* For good measure, we [use the model to
classify](http://en.wikipedia.org/wiki/Naive_Bayes_classifier#Document_Classification)
the held-out test data, and plot a [Precision-Recall
curve](http://en.wikipedia.org/wiki/Precision_and_recall)

![](http://joelgrus.com/wp-content/uploads/2012/02/pr.png "pr")

**Step 7 : Classifying the Data**

Naive Bayes classifier is fast, so it only takes a few seconds to
generate and save *interesting-to-Joel* probabilities for all the
stories in the database.

**Step 8 : Publishing the Data**

This should have been the easiest step, but it caused me a surprising
amount of grief. First I had to decide between

\* publish every story, accompanied by its probability; or\
 \* publish only stories that met some threshhold

In the long term I'd prefer the second, but while I'm getting things to
work the first seems preferable.

My first attempt involved setting up a Twitter feed and using the
Twitter Ruby gem to publish the new stories to it as I scored them. This
worked, but it [wasn't a pleasant way to consume
them](https://twitter.com/#!/joelgrus_hn), and anyway it quickly ran
afoul of Twitter's rate limits.

I decided a blog of batched stories would be better, and so then I spent
several hours grappling with Ruby gems for WordPress, Tumblr, Blogger,
Posterous, and even LiveJournal [!] without much luck. (Most of the
authentication APIs were for more heavy-duty use that I cared about -- I
just wanted to post to a blog using a stored password.)

Finally I got Blogger to work, and after some experimenting I decided
the best approach would be to post once an hour, all the new stories
since the last time I posted. Eventually I realized that I should rank
the stories by *interesting-to-Joel*-ness, so that the ones I'd most
want to read would be at the top:

![](http://joelgrus.com/wp-content/uploads/2012/02/hnj_top.png "hnj_top")

and the ones I want to read least would be at the bottom:

![](http://joelgrus.com/wp-content/uploads/2012/02/hnj_bottom.png "hnj_bottom")

The blog itself is at

<http://joelgrus-hackernews.blogspot.com/>

**Step 9 : Automate**

This part was pretty easy with two cron jobs. The first, once an hour,
goes to the Hacker News API and retrieves all new unknown stories (up to
a limit of like 600, which should never be hit in practice). It then
scores them with the last saved model and adds them to the database. In
practice, the API isn't working half the time.

The second, a few minutes later, takes all the new stories and posts
them to the blog. The end result is a blog of hourly scored digests of
new Hacker News posts.

**Step 10 : Improve the Model**

The model can only get better with more training data, which requires me
to judge whether I like stories or not. I do this occasionally when
there's nothing interesting on Facebook. Right now this is just the
above command-line tool, but maybe I'll come up with something better in
the future.

**Step 11 : Profit**

I'm still trying to figure this one out. If you've got any good ideas,
the code is [here](https://github.com/joelgrus/hackernews).
