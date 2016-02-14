Title: Building a Stupid Data Product, Part 1: The Data (Python)
Date: 2016-02-15 07:00
Category: Python, Hacking, Data, Data Science

(<a href = "">part 2</a>, <a href = "">part 3</a>)

As I'm not working right now, I have a surfeit of time to hack on stupid things.
In particular, it seemed like a good idea to hack together a stupid data product.

Inspiration (if you can call it such) struck when the Allen Institute released
a dataset of <a href="http://allenai.org/data.html">elementary school science questions</a>,
presumably so that people can train computers to answer them. I am not quite so
ambitious, so instead I decided to use them to train a computer to generate
new random bogus elementary school science questions.

Using markov chains to generate text this way isn't particularly exciting, so
I thought I'd also play around with the other parts of building a data product:
creating a backend service that serves up random questions, and creating a
single-page app that allows you to take these random quizzes.

(Code, as always, is on <a href = "https://github.com/joelgrus/science-questions">GitHub</a>.)

If you know me, you're thinking "backend service, that sounds like a job for
Haskell" and also "single-page app, that sounds like a job for PureScript".
You're basically right, with a caveat we'll see later, but in this first blog
post let's just focus on the data piece.

We'll use a dead simple markov chain model. For each word in the dataset, we
make a list of all the words that we see following it. That is, if we had only two
questions: "What is love?" and "What the heck?" then our model would say that
'What' can be followed by either 'is' or 'love'. We generate a sentence by picking
a starting word and repeatedly choosing a random next word (based on the transitions
we learned from the data) until we finish a sentence.

This means our data goal is to generate these transitions. We'll represent them
as `dict`s where the keys are words, and the values are lists of next words:

```python
{ 'What' : ['is', 'the'],
  'is' : ['love'],
  # and so on
}
```

To start with, we can just download the CSV:

![questions]({filename}/images/questions_csv.png)

We only care about the 'question' column, so let's just read that in.
(As always, use `csv.reader`, don't try to parse it by hand!)

```python
with open('questions.csv') as f:
    reader = csv.DictReader(f)
    raw_questions = [row['question'] for row in reader]

# raw_questions[0]
# 'Which property of an object is identified using the sense of smell? (A) color (B) odor (C) temperature (D) weight'
```

Now we're going to actually want *two* markov chain models. If you look at the
data, you'll see that questions and answers look quite different from one another.
So we'll generate one set of "question transitions" and another set of
"answer transitions".

To that end, we need a way to split a `raw_question` into a "question" piece and
several "answer" pieces. This looks like a job for regular expressions. Using the
example above, we might try something like

```python
re.split("\([A-D]\)", raw_question)
```

which looks for the letters A - D in parentheses, and splits the string
where it finds them. Looking at the file,
every question has either 3 or 4 answers, which means that the result of that `split`
should have 4 or 5 elements (including the question text).

Let's see where our regex falls down:

```python
split = "\([A-D]\)"

for q in raw_questions:
    if len(re.split(split, q)) not in [4, 5]:
        print(q)
        break

# answer looks like A. 9 yards B. 18 yards C. 50 yards D. 70 yards
```

So we need a regex for this case, too, how about `"\s[A-D]\.\s"`. If we iterate
this process, we end up with a list of regexes that covers all the questions
(except one that has no answers):

```python
splits = [
  "\([A-D]\)",    # (A) python (B) haskell (C) javascript (D) ruby
  "\s[A-D]\.\s",  #  A. python  B. haskell  C. javascript  D. ruby
  "\s[1-4]\.\s",  #  1. python  2. haskell  3. javascript  4. ruby
  "\s[A-D]\s",    #  A  python  B  haskell  C  javascript  D  ruby
  "\s[FGHJ]\s",   #  F  python  G  haskell  H  javascript  J  ruby
  "\n [A-D]\s"    #   A python
                  #   B haskell
                  #   C javascript
                  #   D ruby
]
```

We're almost ready, the other thing we'll do is use a couple of _sentinels_:

```python
START = "__START__"
STOP = "__STOP__"
```

We'll add a transition from `START` to the first word of every sentence, and a
transition from the last word of every sentence to `STOP`. That way we can generate
sentences using essentially the following logic:

```
word = random_word_after(START)
while word != STOP:
  yield word
  word = random_word_after(word)
```

So, to sum up, our strategy will be:

* collect all of the question "sentences" and answer "sentences" separately
* use the sentences to generate transition `dict`s
* serialize the transitions, so we can use them in other programs

First, the collecting:

```python
questions = []
answers = []

for q in raw_questions:
    for split in splits:
        pieces = [x.strip() for x in re.split(split, q)]
        if len(pieces) in [4,5]:
            questions.append(pieces[0])
            answers.extend(pieces[1:])
            break   # go on to the next raw_question
    else:           # have you ever seen someone use a for .. else loop?
        print(q)    # me neither!
```

Now we have a `list` of questions and a `list` of answers, so let's turn
each into a `dict` of transitions. We'll use another regex to turn each question
(or answer) into words:

```python
re.findall("[^ ?\.,]+|\?|\.|\,", sentence)
```

That regex looks kind of cryptic, but it's just looking to match either

* a period,
* a comma,
* a question mark, or
* a "word" that contains none of the above or spaces

We just need to remember to add the "sentinel" words, and we have our function:

```python
def make_transitions(sentences):
    transitions = defaultdict(list)
    for sentence in sentences:
        # regex looks for "?", ".", "," or groups of characters that aren't
        # any of those, and aren't spaces
        words = [START] + re.findall("[^ ?\.,]+|\?|\.|\,", sentence) + [STOP]
        for prev_word, next_word in zip(words, words[1:]):
            transitions[prev_word].append(next_word)
    return transitions
```

And then we just need to save them for later use:

```python
q_transitions = make_transitions(questions)
a_transitions = make_transitions(answers)

with open('questions.json', 'w') as f:
    f.write(json.dumps(q_transitions))

with open('answers.json', 'w') as f:
    f.write(json.dumps(a_transitions))
```

Now we can generate sentences as above:

```python
def next_word(transitions, word):
    return random.choice(transitions.get(word, [STOP]))

def markov_gen(transitions):
    word = next_word(transitions, START)
    while word != STOP:
      yield word
      word = next_word(transitions, word)  
```

For example, to generate a fake question and four fake answers:

```python
In [56]: ' '.join(markov_gen(q_transitions))
Out[56]: 'For which part of the deepest ?'

In [57]: ' '.join(markov_gen(a_transitions))
Out[57]: 'A deer'

In [58]: ' '.join(markov_gen(a_transitions))
Out[58]: 'Old refrigerators contain genes .'

In [59]: ' '.join(markov_gen(a_transitions))
Out[59]: 'producers'

In [60]: ' '.join(markov_gen(a_transitions))
Out[60]: 'Mount St .'
```

## Next Time

In the <a href = "">next post</a>
we'll build a web service that generates questions on demand.
