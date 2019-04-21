Title: Polyglot Twitter Bot, Part 2: Node.js + AWS Lambda
Date: 2015-12-29 19:00
Category: Code, Twitter, Node, Javascript, AWS, Make_GreatAgain

[The second in an (at least) 6-part series, all code <a href = "https://github.com/joelgrus/polyglot-twitter-bot">on GitHub</a> as always.]

1. <a href="https://joelgrus.com/2015/12/29/polyglot-twitter-bot-part-1-nodejs/">Node.js</a>
2. <b>Node.js + AWS Lambda</b>
3. Python 2.7 + AWS Lambda
4. Purescript
5. Purescript + AWS Lambda
6. Bonus: Purescript + Twitter Streaming

AWS has a recent-ish <a href = "https://aws.amazon.com/lambda/">Lambda</a> product,
which lets you upload functions and then have them run on demand (or on a schedule),
without having to actually run a server. There's a lot of interesting things you
can do with this functionality, one of which is "run a Twitter bot".

These days Lambda allows Node.js, Python, or Java functions, but for now we'll
modify and use the Node.js bot we built <a href="https://joelgrus.com/2015/12/29/polyglot-twitter-bot-part-1-nodejs/">previously</a>.

The only trick is that we need to fit it into the <a href = "http://docs.aws.amazon.com/lambda/latest/dg/programming-model.html">Lambda execution model</a>.

Lambda expects our Node module to export a `handler` function with the following signature:

```js
exports.handler = function(event, context) {
   // do something
};
```

Here `event` contains the parameters for the function invocation,
and `context` contains Lambda-specific details. Our bot function
won't take any parameters, since it has everything it needs
(query, credentials, etc...) hardcoded in it. The `context` object contains
`succeed` and `fail` methods that tell Lambda that the function is done running.
(This is why we included them last time.)

So a handler that would work here is just

```js
exports.handler = function(event, context) {
  searchAndTweet(context.succeed, context.fail);
};
```

Now, if your function doesn't use any fancy libraries, you can simply type the
code into the AWS console. However, here we're using the `twitter` library, so
we can't. Instead we have to create a deployment package, which is just a zip file.

```bash
$ ls
credentials.js  index.js  node_modules  package.json
```

In particular, we need to include the `node_modules` directory, which contains
the Twitter library and its dependencies.

```bash
$ zip -r twitter.zip *
```

This gets me a ~1.3MB zip file. Now go to
<a href="https://console.aws.amazon.com/lambda/">your AWS console</a>
and click "Create a Lambda Function".

<img src="/images/create_a_lambda_function.png">

"Skip" the "select blueprint" step,
give your function a name, and upload the zip file.

The default handler name `index.handler` should work (`index` means to look in
`index.js`, `.handler` means to use the function called that), and then create
or choose a "basic execution" role.

The 128MB should be plenty of memory, but you might want to up the timeout to
10 seconds or so.

<img src="/images/configure_function.png">

Finally, click "Create Function". At this point you want to
"Save and Test" to make sure it works.

Finally, you probably want it to run on a schedule, so choose the "Event Sources"
tab and click "Add event source". Go to "scheduled event" and enable it to run
every 5 minutes (or every 15 if you want).

<img src="/images/every-5-minutes.png">

(I am not much of an <a href="https://aws.amazon.com/lambda/pricing/">AWS pricing</a> guru,
 but my best estimate is that this Lambda function should cost you approximately $0.)

And that's it, your bot is done! Next time we'll do it in Python.
