Title: Vibe Coding 7 -- Human in the Loop as a dspy.Tool
Date: 2025-08-13 12:00
Category: Vibe Coding

As I started to think about my 
[meme-generating agent](https://joelgrus.com/2025/08/12/vibe-coding-6-pymgflip/), I figured that
I might want to allow it to ask clarifying questions.
That makes it not just a multi-turn conversation
(which just requires maintaining a history)
but more like a ReAct agent with a "human in the loop" tool
for asking clarifying questions to the user 
(all in pursuit of a singular goal).
And it wasn't obvious how to do this 
(especially in a webapp, in a console app you can do it in a pretty
 straightforward way).

(I'm sure other people must have done this and written about it, but if so I couldn't find it.)

So I had a fairly long conversation with Web Claude
(don't ask me why I picked him over ChatGPT or Gemini)
about [how one might implement this](https://claude.ai/share/c940432b-b912-4adc-8f18-db93ce45591b)
and ended up with a markdown file explaining what we were hoping
to accomplish and how we planned to it.

I handed that markdown file to claude code, and we got after it.
We built and iterated and built and refactored and changed our design
and built and built. This was an interesting problem for a couple of reasons:

1. It required using Python async, which I am not good at. 
For example, imagine that the agent is running as part of a webapp.
then when the webapp needs human input, it needs to "pause" what it's 
doing, somehow get a request to the user, somehow get a response back,
and then resume. Hence async.
2. Therefore, unlike a lot of this vibecoding stuff, it required some thoughtful and intricate design.

We went through probably 10 different designs.
Each time it was me (not Claude) saying
"that doesn't feel like the right abstraction,
 what about X, Y, or Z?"
Eventually we ended up with something pretty clean.

This is really at the core of what we landed on.
A `HumanInputRequest` is a question and an _awaitable_ response
(here implemented by an asyncio.Future).

```python
class HumanInputRequest:
    def __init__(self, question: str):
        self.question = question
        self._response_future = asyncio.Future()
    
    async def response(self) -> str:
        """Wait for the response to be provided"""
        return await self._response_future
    
    def set_response(self, response: str):
        """Provide the response and notify waiters"""
        self._response_future.set_result(response)
```

We can then define different "human in the loop" tools by
defining "requesters", async functions that take a `HumanInputRequest`
and do [waves hands] something asynchronously.

```python
# A requester is an async function that takes a HumanInputRequest
# and handles the outbound request to humans, allowing them to provide a response.
# It should resolve the request by calling request.set_response(response).
Requester = Callable[[HumanInputRequest], Awaitable[None]]
```

Which leads to a pretty clean "human in the loop" tool:

```python
def human_in_the_loop(requester: Requester) -> dspy.Tool:
    async def ask_human(question: str) -> str:
        request = HumanInputRequest(question)
        
        # Let requester handle the outbound request
        await requester(request)
        
        # Wait for response (resolved by requester or external system)
        response = await request.response()
        return response
    
    return dspy.Tool(ask_human)
```

One very simple use case (for which this is overkill) is a single-player
console app. In that case the requester can just call `input()` synchronously and set the response:

```python
async def console_requester(request: HumanInputRequest):
    response = input(f"\n{request.question}\n> ")
    request.set_response(response)

tool = human_in_the_loop(console_requester)
```

A more interesting case is the web app, where a lot of things need to happen before the response comes back. For that case we implemented a simple "work queue" requester:

```python
def create_queue_requester(request_queue: asyncio.Queue, pending_requests: dict):

    async def queue_requester(request: HumanInputRequest):
        # Generate a unique ID for this request
        request_id = str(uuid.uuid4())
        
        # Store in pending requests for response resolution
        pending_requests[request_id] = {
            'request': request,
            'question': request.question,
            'sent': False
        }

        # Push to the request queue         
        await request_queue.put({
            'type': 'human_input',
            'id': request_id,
            'question': request.question
        })

        # Mark as sent to avoid duplicate sends
        pending_requests[request_id]['sent'] = True
    
    return queue_requester

queue_requester = create_queue_requester(my_queue, my_dict)
tool = human_in_the_loop(queue_requester)
```

Now in (say) your web app you can connect the queue to send server-sent events 
to the browser, and you can have a secondary endpoint that finds the request
in the dict, sets its value, and evicts it from pending.

(You would have to harden this up a bunch for a real production system, but it's good enough for our demo.)

This is now pretty easy. Our console app can just use a ReAct agent:

```python
class Pizza(TypedDict):
    size: str
    toppings: list[str]
    special_instructions: str | None

class OrderPizza(dspy.Signature):
    """
    An agent that can ask clarifying questions about a pizza order.
    It can handle multiple pizzas and special instructions.
    """
    customer_request = dspy.InputField()
    pizzas: list[Pizza] = dspy.OutputField()

agent = dspy.ReAct(
    signature=OrderPizza,
    tools=[human_in_the_loop(console_requester)],
    max_iters=6
)
```

And will ask clarifying questions to help us order a pizza:

```plaintext
What is your order?
(Type 'quit' to exit)
> I need a small pizza with rocks on it

🤖 Agent is thinking about: 'I need a small pizza with rocks on it'
The agent may ask you questions during its reasoning process...

🤔 You mentioned 'rocks' on your pizza. Could you please clarify what you mean by that? We don't typically offer rocks as a topping.

> I want rocks on it

🤔 I understand you want 'rocks' on your pizza. Could you describe what kind of 'rocks' you are looking for? For example, are you referring to a specific ingredient that might sound like 'rocks', or something else entirely?

> rocks like you'd find on a hill

🤔 I understand you're looking for actual rocks on your pizza. Unfortunately, we cannot put inedible items like rocks on our pizzas for safety and health reasons. Is there a different topping you had in mind, or would you like to order the small pizza without the 'rocks'?

> can you use meatballs to make "rocks"

🤔 Yes, we can certainly add meatballs to your pizza! To clarify, would you like whole meatballs, or would you prefer them crumbled to resemble 'rocks' more closely? Also, just to confirm, you'd like a small pizza with meatballs, and no other specific toppings unless you mention them?

> small pizza with meatballs crumbled to resemble rocks

✅ Order: [{'size': 'small', 'toppings': ['meatballs'], 'special_instructions': 'meatballs crumbled to resemble rocks'}]
```

And the web app behaves similarly:

![pizza-agent]({static}images/pizza-agent.png)

Despite this being a silly example, this is actually a pretty neat
demonstration of the DSPy / ReAct workflow. I didn't have to program
anything about the flow of the conversation (e.g. "next ask for the pizza size").

Instead I gave it a structured output format ("I want a list of pizzas, each of which has the following fields") and a tool to ask clarifying
questions, and then the ReAct loop and LLM took care of deciding what questions to ask until it got all the information it needed. 
That's actually really cool!

Anyway, this was pretty satisfying to puzzle out, and hopefully it helps someone else. 

As always, the code is [on GitHub](https://github.com/joelgrus/human-in-the-loop-dspy-tool).