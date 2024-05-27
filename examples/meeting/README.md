Idea:
- create an example, where the dev can instruct the LLM to response a system prompt which instructs an LLM to respond within JSON
- the example could contain a message history for the context to know what is needed as information
- the LLM which creates the instruction uses this message history as a context to create the "perfect" system prompt to get the best out of the LLM
- The "instruct" LLM will be displayed the JSON schema and should use it as well to instruct the LLM


This example can show how an "agent" can be built by the dev by using `ollama-instructor` only and not relying on an agent framework. And it could show that smaller LLMs are also capable of doing complex JSON responses.

# Meeting

This example showcases the processing of a big amount of text as it can appear in a meeting transcript. 

The possible processing fields are:
- summarizing the meeting
- separating the meeting into key parts/topics and summarize those
- extract important information and action items from the meeting. List further topics regarding the meetings context (what was missing? what could cause problems?)
- create todos based on the action items and enrich them with context and additional information (i.e. assigned person, due date, priority, suggestions, etc.)

## Files

### persons.json

This file contains information about the persons in the meeting. It can be used to enrich the context for the LLM to perform better in its tasks.

### conversation.md

This file contains the meeting transcript. It can be used to summarize the meeting, extract information and action items from it, etc. It displays the main knowledge base for the tasks.

### meeting.py

The Python script contains the code and logic to process the meeting transcript as described above. It uses the `ollama-instructor` library to instruct the LLM to perform these tasks and is what you can call an `agentic` workflow.


## Workflow

The workflow is as follows:
1. The script reads the conversation.md file and extracts the meeting transcript from it.
2. (The script will be embedded and the embeddings are stored into a vector db)
3. 
