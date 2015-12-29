Title: Polyglot Twitter Bot, Part 1: Node.js
Date: 2015-12-29 12:00
Category: Code, Twitter, Node, Javascript, AWS, Make_GreatAgain

[The first in an (at least) 6-part series, all code <a href = "https://github.com/joelgrus/polyglot-twitter-bot">on GitHub</a> as always.]

1. <b>Node.js</b>
2. Node.js + AWS Lambda
3. Python 2.7 + AWS Lambda
4. Purescript
5. Purescript + AWS Lambda
6. Bonus: Purescript + Twitter Streaming

Like most of you, I've long dreamed of making a Twitter bot.
And also like most of you, I've been doing a lot of
<a href="https://nodejs.org/en/">Node.js</a> recently. So I thought I'd take the first stab
at writing my Twitter bot in Node. (Also, this will lay the groundwork for doing it in
Purescript later.)

In particular, I wanted to create the <a href = "https://twitter.com/make_greatagain">make_greatagain</a>
bot, which would look for tweets containing "MAKE ___ GREAT AGAIN" constructions
and retweet them. (But which skips tweets containing "MAKE AMERICA GREAT AGAIN",
I'm looking for riffs on the original, not the original itself.)

<a class="twitter-timeline" href="https://twitter.com/make_greatagain" data-widget-id="681668898454765568">Tweets by @make_greatagain</a>
<script>!function(d,s,id){var js,fjs=d.getElementsByTagName(s)[0],p=/^http:/.test(d.location)?'http':'https';if(!d.getElementById(id)){js=d.createElement(s);js.id=id;js.src=p+"://platform.twitter.com/widgets.js";fjs.parentNode.insertBefore(js,fjs);}}(document,"script","twitter-wjs");</script>

To start with, you should probably have Node installed. (I'll wait.)
Then create a directory, and initialize a new project:

```bash
mkdir twitter-bot-node
cd twitter-bot-node
npm init
```

Just accept all the default options for `npm init`, I don't know what they mean
either.

Now, if we're going to talk to Twitter, we should install the
<a href = "https://www.npmjs.com/package/twitter">Node Twitter module</a>.

```bash
npm install twitter --save
```

At this point you should create a Twitter account for your bot and get its
credentials. After creating the account and logging in, go to <a href = "https://apps.twitter.com">apps.twitter.com</a>
and click on "Create New App". Give it a name and a description, and accept the terms of service.
Then go to the "Keys and Access Tokens" tab and click "Create My Access Token".
You should now have a consumer key, a consumer secret, an access token, and an
access token secret. We need those, but KEEP THEM SECRET.

Now, we're ready to create our `index.js`.  We start by loading the Twitter library
and initializing it with our credentials:

```js
var Twitter = require('twitter');
var client = new Twitter({
  consumer_key: "...",
  consumer_secret: "...",
  access_token_key: "...",
  access_token_secret: "..."
});
```

NOTE: if you are committing this code to GitHub, DO NOT CHECK IN THE CREDENTIALS.
One approach is to stick them in `credentials.js`, like

```js
module.exports = {
  consumer_key: "...",
  consumer_secret: "...",
  access_token_key: "...",
  access_token_secret: "..."
};
```

and then in `index.js` just do

```js
var credentials = require('./credentials');
var client = new Twitter(credentials);
```

and then make sure to add `credentials.js` to your `.gitignore`.

Now, we want to find Tweets of the given form. For my example, that's

```js
var query = 'make "great again" -america -filter:retweets';
var rgx = /make .* great again/i;
```

(Hopefully, your Twitter bot will do something different.)

The `query` is the actual query we'll send to Twitter. It looks for Tweets that
contain both "make" and "great again" but not "america". And it ignores retweets.
Since that search could (in theory) return irrelevant tweets
(e.g. "great again doesn't make sense"), there's also a regex that we'll use
as a client-side check.

Now, the Node model is asynchronous, which means we need to program with callbacks.
That is, to search, we need to do something like

```js
client.get('search/tweets', {q: "node.js"}, function(err, tweets, response) {
  if (err || !tweets.statuses) {
    console.log(err);
  } else {
    tweets.statuses.forEach(function(tweet) {
      console.log(tweet.user.screen_name + " " + tweet.text);
    });
  }
});
```

This code will kick off a search for "node.js" and then immediately go on to
whatever code comes next. Meanwhile, whenever the search returns,
the provided callback will be called, either logging the error or
printing out the returned tweets.

Now in our code we want the callback to retweet each of the returned tweets.
However, if we try to retweet a tweet we've already retweeted, we'll get an error.
This means we either need to keep track of all the tweets we've already retweeted
or else handle those errors intelligently. The second is a lot easier.

In order to retweet, we just need to post the tweet `id` to the retweets endpoint.
If you inspect the returned tweets, they have both an `id` field (which is a number)
and an `id_str` field (which is a string). For precision-related reasons (I assume),
Javascript mangles the numeric ids, so we'll need to use the string version.

All of which results in a function that looks like

```js
// Runs a Twitter search for the specified `query` and retweets all the results.
function searchAndTweet(succeed, fail) {
  console.log("search and tweet");
  client.get('search/tweets', {q: query, count: 15}, function(err, tweets, response) {
    if (!tweets.statuses) {
      fail(err);
    }

    tweets.statuses.forEach(function(tweet) {
      // Make sure we match the regex.
      var match = tweet.text.match(rgx);
      if (match) {
        var tweetId = tweet.id_str;
        client.post('statuses/retweet/' + tweetId, function(err, tweet, id) {
          // Will return an error if we try to retweet a tweet that we've already
          // retweeted.
          console.log(err || tweet.text);
        });
      } else {
        // consider doing something for no match
      }
    });
    succeed("success");
  });
}
```

Why do we pass in the `succeed` and `fail` callbacks? That's a story for the next
post. (Spoiler: it involves AWS Lambda.) In the meantime, you can just pass in `console.log` for both.

Now, all that's left is to run your Twitter bot. We can use `setInterval` to make
it run every 5 minutes:

```js
setInterval(function() {
  searchAndTweet(console.log, console.log);
}, 5 * 60 * 1000);
```

And then if you simply

```bash
$ node index.js
```

your bot will start running. Of course,
you probably don't want to keep it running locally on your computer all the time.
We'll deal with that in the next post.
