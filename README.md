<img width="1080" height="1673" alt="image" src="https://github.com/user-attachments/assets/c0493414-0719-4bb9-be7f-4e464eee5b02" />

(real screenshot of a real guy getting catfished with this code (fully ai), 100% unattended)
Have you ever tried catfishing your friend but given up after some time because it was too much commitment to keep texting him?

This is the perfect solution. 


Here's what this package does:
1. It uses the InstagrAPI to connect to your catfish account.
2. For the specific username that you are trying to catfish, it goes ahead and it starts downloading every single message one by one.
3. It takes all those messages and puts everything into the database.
4. If you want, it can download all the medias also, such as images, videos, and reels.
5. It can additionally send those reels to an LLM to summarize it with a textual description

The next step is extract all the facts and memories and everything that has been discussed
1. We basically split the entire chat into one texting session, usually somewhere between 30 minutes. 
2. There is a complex algorithm which makes sure that it clubs everything related to the same context together in one session. 
3. After this every session is sent to an LLM. 
4. The LLM extracts various information, such as memories, events, and chat logs, and summarizes the specific session. 
5. This happens for every single session one by one. 
6. After this there's a second turn which takes all the sessions and then combines them into one final source of truth, which I call Facts. 
7. These evolve over time and hence everything is there in Facts


Now we have to figure out the personality of our chatbot. The whole purpose is so we are indistinguishable from a real human.
For every session, just like we extracted memories, we extract specific texting style, vocabulary, the way you talk, how you send burst messages, etc., every single thing related to the personality. Then we combine all of those and make one final doc, which gets stored.
This specific doc has all the necessary requirements for an LLM to precisely behave and impersonate a real human. It has all the little details, every single piece of information:
• the way you talk
• what your lingo is
• what your vocabulary is
• the way you text
• how hyper you are
• how excited you get
• in what scenario you behave one way and in another scenario you behave another way
This is the most in-depth prompt for your LLM


Sometimes chat becomes very huge and Instagram pagination takes a lot of time to load. It's not really easy to semantically search through it either using their search.
The simplest solution was that if we are archiving the chat anyways, we create a viewer that lets us render all the chats and watch what's going on live. For our specific chat we can open localhost and view how every single chat is coming in. They update and they scroll at blazing speeds. Because it's Insta and there are a lot of reels and posts and media sent, everything is automatically embedded and viewable right there on the website (without the need to go to Instagram, irrespective of whether you decided to download the reels or not)

Now the most crucial and the most important part: how does the LLM actually text?
There are four different layers with four different models that handle various paths:
1. The orchestrator is the one that receives the context and receives the messages. Messages are batched because some people like to send spam messages. They're all clubbed together under a small debounce time and they're all sent to the orchestrator. The orchestrator can choose whether it has enough information to respond right away or it needs memories.
2. The memory LLM has a job to go search the database, extract the memories that the orchestrator needs, and return them to him so it has enough data to draft a response.
3. The drafted response from the orchestrator is sent to a Tone LLM. The Tone generator takes the already mapped personality and, based on that, takes the orchestrator's response and Tone Setup makes it exactly indistinguishable from a real human.
4. There is a Guard LLM. This LLM makes sure that we don't accidentally reveal that we are an AI model. It makes sure to eliminate every single response, such as "I'm an AI" or, let's say, "that 7,400 × 2,400, a normal human won't respond to that" or "assistant-type behaviors," etc. All of that is eliminated.

Only after this entire loop is verified by the guard algorithm is the message allowed to be sent. The way we handle sending is through the same library that allows us to intercept live messages and with a workaround we can get the typing indicator of the other person.
What we do is that we take the response that this AI has generated. The response is basically what messages to respond with and how many messages. In case there are reactions to be added to the received messages, we can add those. Whether we are supposed to reply to a message, we can tag it as a reply so Instagram renders it as a reply.
All of this is passed on. We render all of this and we send this. We add a fake typing indicator so we can simulate the typing bubble that shows to the other person and we wait for an exact time before responding so it looks like a real human is typing it

We keep going back and forth and congratulations we have successfully made a catfish account that's purely by AI. A critical note is that this requires you to have already textured or established some amount of personality so that way we can extract the already existing personality and thus mimic it. Optionally this is the first. If we're trying to catfish a person without sending him a real message by ourselves, we can draft a personality style by ourselves and we can put it there instead, which would be followed. However this is not recommended

The entry point is chat.py. Simply run it but before that go to config.py and set up all the variables as needed and set up the Instagram session ID.
The way you obtain this ID is by logging in to instagram.com from your account. Go into the browser, inspect tools, and take the application cookie, which is called the IG session ID. You're supposed to take that and paste it in your environment variables and take your Open Router API key and paste that too in the environment variables. Configure your config and just hit run.
The code is automatically going to be set up and it's automatically going to initialize all the dbs if required. It is going to download all the messages. It's going to increment every time you run it if messages are only downloaded already. It's automatically going to start replying to the same thread ID that you set up with the same username of the person that we've already set up.
