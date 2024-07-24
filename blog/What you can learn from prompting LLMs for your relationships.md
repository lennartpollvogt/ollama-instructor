# What you can learn from prompting LLMs for you relationships

With the emergence and rise of Large Language Models (LLM) like GPT, Llama, Mistral and others, a new field in tech was available for everbody, which you can call awkwardly "**programming with natural language**". But more well known is the term **prompt engineering**. For this blog post I was asking a LLM to tell me what **prompt engineering** is and it came up with the following:

> "*Prompt engineering is the practice of refining and optimizing prompts given to generative artificial intelligence (AI) models to produce desired outputs. This technique is crucial for enhancing the accuracy and effectiveness of AI-generated content, whether it's text, images, or audio. By carefully crafting the input prompts, users can guide AI models to generate specific results tailored to their needs. This process involves adjusting the wording, structure, and context of the prompts to achieve the best possible outcome from the AI model. Prompt engineering is applicable across various domains, including text generation, image synthesis, and audio production, making it a versatile tool for anyone interacting with generative AI systems.*" (created with Phind-70B on [Phind.com](https://www.phind.com))

The prompt was quite simple, like "*create a short description of what prompt engineering is*". You couldn't say, that this contains any advanced prompting technique since all I wanted was to have a general overview of what **prompt engineering** is and I would say in this case the LLM nailed it. However, I wasn't lucky to receive such a good answer because this one was generated under some circumstances:

1. it was a clear question that could hardly be misinterpreted since prompt engineering is a precise term
2. the LLM was quite large and well trained in general topics and generating answers
3. the LLM was embedded in a system that enabled it to access knowledge resources on the internet to gain more context to a question

> *Here is the link if you want try out [**Phind**](https://www.phind.com) by your own.*

If you are already familiar with some LLMs then you may know that under different circumstances another LLM or even the same LLM would have came up with another answer. In the best case it would be a similar answer, but depending on the dataset it was trained on and the in- or availability to knowledge resources (e.g. RAG or internet search), the LLM could have generated an answer were it hallucinates about **prompt engineering**. 
Hallucination is something we really want to avoid. Especially if we want to build an application which will be used by our costumers or in our intern processes, then we have to make sure the output is reliable. 

> *In the following I will use the more general term **output** instead of **answer** as it is not always a question and answer scenario when we interact with a LLM. LLMs are already used to generate processable outputs which can be used by functions and therefore they are somtimes part of the backend too.*

Getting reliable outputs from a LLM can be changelling. And you will not find the "**one fits it all prompt**" or a setup to meet all your needs. As LLMs are already used for a broad range of tasks like summarizing text, calling functions, extracting data, etc., the requirements change with every task and need therefore a different prompting. But as this field of tech gained so much attention over the last years the computer science published a lot of research, and therefore, there are already some best practices. Those best practices combine different prompting techniques and tools to squeeze out the best possible output from the LLM. These six highly recommended prompting techniques are mentioned in a paper of [An Empirical Categorization Of Prompting Techniques For Large Language Models: A Practitioner's Guide](https://arxiv.org/pdf/2402.14837):

1. **Write clear instructions**
	- include details in your query
	- define desired persona
	- use delimiters for distinct parts
	- specify desired output format
2. **Provide relevant context**
	- use a reference text
	- supply background information
	- describe the problem
	- provide auxillary examples
3. **Split complex tasks**
	- use intent classification
	- summarize/filter long dialouges
	- summarize documents piecewise
	- give steps for the model to follow
4. **Give the model time to "think"**
	- require explanations for responses
	- use inner monologues or queries
	- request self-evaluation of output
	- ask follow-up questions
5. **Use external tools** (PRO)
	- provide access to external files
	- utilize web browsing capabilities
	- request code execution via APIs
	- give access to relevant plugins
6. **Test changes systematically** (DEVELOPMENT)
	- adjust prompts incrementally
	- evaluate intermediate outputs
	- start with simplified queries
	- ask related questions

> I highly recommend having a look into the linked paper!

But don't be a fool to think, that you will get everything right in the first try. Working with LLMs needs some iterations where you adjust the prompt, try out different techniques or tools and get a feeling for the weaknesses and strengths of the LLM you are working with. And be sure, if something works with one LLM it doesn't mean that it will work for another one as well. In some cases you will have to adjust the prompting system you created to fit to the other LLM. I just want you to be aware of that.

## Making the connection

As you have now a rough overview on what **prompt engineering** is and how you apply it, you might think at this point: "*What does this has to do with the title of this post?*". And yes, I owe you an explanation.

As I started to read about and try out working with LLMs at work and in my spare time, I found more and more parallels with the relationship I've been in for about 12 years. Based on my observations, I can say that there are a few key factors to consider if you want to have a healthy relationship. And by comparing them with the best practices above, the parallels became somehow obvious:

**Best practices**:

| LLM                            | Relationship                                                                                       |
| :----------------------------- | :------------------------------------------------------------------------------------------------- |
| Write clear instructions       | Express yourself honestly and clearly                                                              |
| Provide relevant context       | Be aware of your feelings and needs, and be able to express them without intentionally hurt anyone |
| Split complex tasks            | Don't overburden your partner                                                                      |
| Give the model time to "think" | Give room to breathe and think                                                                     |
| Use external tools             | Seek external support when needed                                                                  |
| Test changes systematically    | Regularly reevaluate and adapt you relationship dynamics in collaboration with your partner        |

I am aware that in contrast to an interaction with Artificial Intelligent (AI) systems like LLMs, human relationships have far more complexity and depth. The analogy was driven by drawing attention to fundamental aspects of effective communication that can enhance both AI usability and relationship satisfaction.

I hope reading this was fun, so, here is my controversal take: people who are good at relationships have an advantage in **prompt engineering** as opposed to those who have a toxic relationship.