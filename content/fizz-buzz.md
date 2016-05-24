Title: Fizz Buzz in Tensorflow
Date: 2016-05-23 12:00
Category: Tensorflow, Python, Interviews, Coding

<b>interviewer:</b> Welcome, can I get you coffee or anything? Do you need a break?

<b>me:</b> No, I've probably had too much coffee already!

<b>interviewer:</b> Great, great. And are you OK with writing code on the whiteboard?

<b>me:</b> It's the only way I code!

<b>interviewer:</b> ...

<b>me:</b> That was a joke.

<b>interviewer:</b> OK, so are you familiar with "fizz buzz"?

<b>me:</b> ...

<b>interviewer:</b> Is that a yes or a no?

<b>me:</b> It's more of a "I can't believe you're asking me that."

<b>interviewer:</b> OK, so I need you to print the numbers from 1 to 100, except that
if the number is divisible by 3 print "fizz", if it's divisible by 5 print "buzz",
and if it's divisible by 15 print "fizzbuzz".

<b>me:</b> I'm familiar with it.

<b>interviewer:</b> Great, we find that candidates who can't get this right don't do well here.

<b>me:</b> ...

<b>interviewer:</b> Here's a marker and an eraser.

<b>me:</b> [thinks for a couple of minutes]

<b>interviewer:</b> Do you need help getting started?

<b>me:</b> No, no, I'm good. So let's start with some standard imports:

```python
import numpy as np
import tensorflow as tf
```

<b>interviewer:</b> Um, you understand the problem is _fizzbuzz_, right?

<b>me:</b> Do I ever. So, now let's talk models. I'm thinking a simple multi-layer-perceptron
with one hidden layer.

<b>interviewer:</b> Perceptron?

<b>me:</b> Or neural network, whatever you want to call it.
We want the input to be a number, and the output to be the correct "fizzbuzz"
representation of that number. In particular, we need to turn each input into a
vector of "activations". One simple way would be to convert it to binary.

<b>interviewer:</b> Binary?

<b>me:</b> Yeah, you know, 0's and 1's? Something like:

```python
def binary_encode(i, num_digits):
    return np.array([i >> d & 1 for d in range(num_digits)])
```

<b>interviewer:</b> [stares at whiteboard for a minute]

<b>me:</b> And our output will be a one-hot encoding of the fizzbuzz representation
of the number, where the first position indicates "print as-is", the second
indicates "fizz", and so on:

```python
def fizz_buzz_encode(i):
    if   i % 15 == 0: return np.array([0, 0, 0, 1])
    elif i % 5  == 0: return np.array([0, 0, 1, 0])
    elif i % 3  == 0: return np.array([0, 1, 0, 0])
    else:             return np.array([1, 0, 0, 0])
```

<b>interviewer:</b> OK, that's probably enough.

<b>me:</b> That's enough setup, you're exactly right. Now we need to generate some training data. It would be
cheating to use the numbers 1 to 100 in our training data, so let's train it on
all the remaining numbers up to 1024:

```python
NUM_DIGITS = 10
trX = np.array([binary_encode(i, NUM_DIGITS) for i in range(101, 2 ** NUM_DIGITS)])
trY = np.array([fizz_buzz_encode(i)          for i in range(101, 2 ** NUM_DIGITS)])
```

<b>interviewer:</b> ...

<b>me:</b> Now we need to set up our model in tensorflow. Off the top of my head I'm
not sure how many hidden units to use, maybe 10?

<b>interviewer:</b> ...

<b>me:</b> Yeah, possibly 100 is better. We can always change it later.

```python
NUM_HIDDEN = 100
```

We'll need an input variable with width NUM_DIGITS, and an output variable
with width 4:

```python
X = tf.placeholder("float", [None, NUM_DIGITS])
Y = tf.placeholder("float", [None, 4])
```

<b>interviewer:</b> How far are you intending to take this?

<b>me:</b> Oh, just two layers deep -- one hidden layer and one output layer.
Let's use randomly-initialized weights for our neurons:

```python
def init_weights(shape):
    return tf.Variable(tf.random_normal(shape, stddev=0.01))

w_h = init_weights([NUM_DIGITS, NUM_HIDDEN])
w_o = init_weights([NUM_HIDDEN, 4])
```

And we're ready to define the model. As I said before, one hidden layer,
and let's use, I don't know, ReLU activation:

```python
def model(X, w_h, w_o):
    h = tf.nn.relu(tf.matmul(X, w_h))
    return tf.matmul(h, w_o)
```

We can use softmax cross-entropy as our cost function and try to minimize it:

```python
py_x = model(X, w_h, w_o)

cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(py_x, Y))
train_op = tf.train.GradientDescentOptimizer(0.05).minimize(cost)
```

<b>interviewer:</b> ...

<b>me:</b> And, of course, the prediction will just be the largest output:

```python
predict_op = tf.argmax(py_x, 1)
```

<b>interviewer:</b> Before you get _too far_ astray,
the problem you're _supposed to be_ solving is
to generate fizz buzz for the numbers from 1 to 100.

<b>me:</b> Oh, great point, the `predict_op` function will output a number from 0 to 3,
but we want a "fizz buzz" output:

```python
def fizz_buzz(i, prediction):
    return [str(i), "fizz", "buzz", "fizzbuzz"][prediction]
```

<b>interviewer:</b> ...

<b>me:</b> So now we're ready to train the model. Let's grab a tensorflow session
and initialize the variables:

```python
with tf.Session() as sess:
    tf.initialize_all_variables().run()
```

Now let's run, say, 1000 epochs of training?

<b>interviewer:</b> ...

<b>me:</b> Yeah, maybe that's not enough -- so let's do 10000 just to be safe.

And our training data are
sequential, which I don't like, so let's shuffle them each iteration:

```python
    for epoch in range(10000):
        p = np.random.permutation(range(len(trX)))
        trX, trY = trX[p], trY[p]
```

And each epoch we'll train in batches of, I don't know, 128 inputs?

```python
BATCH_SIZE = 128
```

So each training pass looks like

```python
        for start in range(0, len(trX), BATCH_SIZE):
            end = start + BATCH_SIZE
            sess.run(train_op, feed_dict={X: trX[start:end], Y: trY[start:end]})
```

and then we can print the accuracy on the training data, since why not?

```python
        print(epoch, np.mean(np.argmax(trY, axis=1) ==
                             sess.run(predict_op, feed_dict={X: trX, Y: trY})))
```

<b>interviewer:</b> Are you serious?

<b>me:</b> Yeah, I find it helpful to see how the training accuracy evolves.

<b>interviewer:</b> ...

<b>me:</b> So, once the model has been trained, it's fizz buzz time. Our input should
just be the binary encoding of the numbers 1 to 100:

```python
    numbers = np.arange(1, 101)
    teX = np.transpose(binary_encode(numbers, NUM_DIGITS))
```

And then our output is just our `fizz_buzz` function applied to the model output:

```python
    teY = sess.run(predict_op, feed_dict={X: teX})
    output = np.vectorize(fizz_buzz)(numbers, teY)

    print(output)
```

<b>interviewer:</b> ...

<b>me:</b> And that should be your fizz buzz!

<b>interviewer:</b> Really, that's enough. We'll be in touch.

<b>me:</b> In touch, that sounds promising.

<b>interviewer:</b> ...

# Postscript

I didn't get the job. So I tried actually running this
(<a href="https://github.com/joelgrus/fizz-buzz-tensorflow">code on GitHub</a>),
and it turned out it got some of the outputs wrong! Thanks a lot, machine learning!

```python
In [185]: output
Out[185]:
array(['1', '2', 'fizz', '4', 'buzz', 'fizz', '7', '8', 'fizz', 'buzz',
       '11', 'fizz', '13', '14', 'fizzbuzz', '16', '17', 'fizz', '19',
       'buzz', '21', '22', '23', 'fizz', 'buzz', '26', 'fizz', '28', '29',
       'fizzbuzz', '31', 'fizz', 'fizz', '34', 'buzz', 'fizz', '37', '38',
       'fizz', 'buzz', '41', '42', '43', '44', 'fizzbuzz', '46', '47',
       'fizz', '49', 'buzz', 'fizz', '52', 'fizz', 'fizz', 'buzz', '56',
       'fizz', '58', '59', 'fizzbuzz', '61', '62', 'fizz', '64', 'buzz',
       'fizz', '67', '68', '69', 'buzz', '71', 'fizz', '73', '74',
       'fizzbuzz', '76', '77', 'fizz', '79', 'buzz', '81', '82', '83',
       '84', 'buzz', '86', '87', '88', '89', 'fizzbuzz', '91', '92', '93',
       '94', 'buzz', 'fizz', '97', '98', 'fizz', 'fizz'],
      dtype='<U8')
```

I guess maybe I should have used a deeper network.
