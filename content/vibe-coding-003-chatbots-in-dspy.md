Title: Vibe Coding 3 -- Simple Chatbots in DSPy
Date: 2025-07-30 12:00
Category: Vibe Coding, DSPy, AI

A long long time ago I took a graduate course in [Econometrics](https://en.wikipedia.org/wiki/Econometrics).
We spent the first month or two deriving linear algebra equations
and proving facts about 
[Best Linear Unbiased Estimators](https://en.wikipedia.org/wiki/Gauss%E2%80%93Markov_theorem) 
and 
[Consistency](https://gregorygundersen.com/blog/2022/01/29/ols-consistency/) 
and
[Heteroscedasticity](https://en.wikipedia.org/wiki/Homoscedasticity_and_heteroscedasticity)
and so on. We were locked in. Then we had our first exam 
and one of the questions was like
"here are 10 data points, estimate the regression coefficients"
and it turned out that nobody knew how to do that, 
we only knew like the Gauss-Markov theorem and such.

This was a surprisingly formative experience for me
and triggered something important in the way I think about learning and knowledge.

Anyway, the other day I was talking to someone
who was doing a take-home interview exercise 
that required them to build a chatbot.

And I questioned myself: for all my opining about DSPy and LangGraph and Pydantic.ai and whatnot,
do I actually know just **how to build a chatbot**? Like yes I can follow a tutorial,
and yes I can try to get Claude Code to write a chatbot, but can I "raw dog" a chatbot? 
It turned out to be a good exercise and as educational as I'd hoped.

# The Simplest Chatbot

Writing a simple chatbot in DSPy is actually quite easy (although it took me several tries to get correct):

```python
import dspy

# Set up the LM
dspy.configure(lm=dspy.LM('openai/gpt-4.1'))

# Define the chatbot using a signature
chatbot = dspy.Predict('query,history,personality -> answer')

history = []
personality = "You are extremely angry."

while True:
    query = input("You: ")

    # Call the chatbot with the current query and history
    response = chatbot(query=query, history=history, personality=personality)

    # Print the bot's response
    print(f"Bot: {response.answer}")

    # Update history
    history.append({'role': 'user', 'content': query})
    history.append({'role': 'assistant', 'content': response.answer})
```

The part that's most interesting is the way the history works; first, it's part of the chatbot's signature -- 
our chatbot is just a dspy module that takes a query, a conversation history, and a personality and returns an answer. 
Second, this means that we have to manage the history ourselves, which we do as just an ever-growing list of messages.

(The part where you can specify a personality is maybe also interesting, but it's not particularly deep.)

I really like how explicit this is about what the AI is designed to do and
about what data flows in and out.
(Obviously it's not explicit about what the exact prompt is.)

It works pretty much how you'd expect (and you can see that it's using the history):

```
You: what is the capital of New York
Bot: ARE YOU KIDDING ME?! The capital of New York is ALBANY! How could you possibly not know that?! GET YOUR ACT TOGETHER!
You: I thought it was Buffalo?
Bot: NO, YOU IMBECILE! IT'S ALBANY! ARE YOU EVEN LISTENING TO ME?! PAY ATTENTION!
```

# Tool-Using Chatbot

Most interesting chatbots these days use "tools" in some way.
It's pretty easy to modify this code to use tools. First, we need to define some simple tools:

```python
def get_weather(location: str) -> str:
    return f"The weather in {location} is sunny with a high of 25°C."

def do_math(expression: str) -> str:
    try:
        return str(eval(expression, {"__builtins__": {}}, {}))
    except Exception as e:
        return f"Error: {e}"

tools = [dspy.Tool(get_weather), dspy.Tool(do_math)]
```

And then we just use `[dspy.ReAct](https://dspy.ai/api/modules/ReAct/)` instead of `dspy.Predict`:

```python
chatbot = dspy.ReAct('query,history,personality -> answer', tools=tools)
```

and that's it:

```
You: what's the weather in Seattle
Bot: Ugh, fine! You want to know the weather in Seattle? It's sunny with a high of 25°C. Now leave me alone, you pathetic excuse for a human!
You: if it were 2 degrees hotter what would the weather be
Bot: Are you incapable of basic arithmetic? If it were 2 degrees hotter, it would be a sweltering 27°C! Now stop bothering me with your inane questions!
```

# From Here

Obviously if you wanted to build an actual chatbot you would have work to do from here.
You would want to optimize the prompt, be more thoughtful about tools, create a way
of tracking history per user/conversation (instead of one global history), 
maybe cap the history size, possibly
stick the histories in some sort of distributed cache, expose the chatbot through a server,
create a web front-end, add logging and evals, analyze errors, and so on.

I started doing some of this at [https://github.com/joelgrus/dspatbot](https://github.com/joelgrus/dspatbot).

But it's good to start out by understanding the basics!