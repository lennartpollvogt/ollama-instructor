# Image captioning with `ollama-instructor`

> **Note**: This example was created based on an issue by [svjack](https://github.com/svjack) ([Issue](https://github.com/lennartpollvogt/ollama-instructor/issues/2)). While this example is performed with the LLaVA:13b vision model, this post contains at the end an additional approach with a smaller model to run such tasks on hardware with less performance.

Before we start with a code example we should explain what image captioning is and what are its use cases.

### **Image captioning** 

**Image captioning** is the process of generating a textual description for an image. This task lies at the intersection of computer vision and natural language processing. Image captioning systems analyze the visual content of an image and produce a descriptive sentence that captures the key elements and context of the image.

### Applications of Image Captioning

The list below is just a tiny sample of possible applications where image captioning is used:
1. **Accessibility**: Helps visually impaired individuals understand the content of images on the web by providing text descriptions.
2. **Content Management**: Facilitates the organization and retrieval of images in large databases by automatically generating metadata. This can as well be used for Retrieval Augmented Generation (RAG) systems.
3. **Social Media**: Enhances user experience by automatically suggesting captions for photos, aiding in content creation.
4. **E-commerce**: Improves product descriptions by generating detailed captions for product images, aiding in better search and discovery.

### Challenges of image captioning

Working with generative AI comes with a few challenges that we need to be aware of in order to adequately address them. This is also the case when creating image captions. The following list points out a few pitfalls that need to be considered when creating image captions and to have the right strategies. 

- **Complexity**: Dealing with ambiguous or complex scenes where multiple objects may be relevant but difficult to describe accurately in one sentence.
- **Context Understanding**: Capturing the context and relationships between objects in an image.
- **Diversity of Descriptions**: Generating varied and natural descriptions for the same image.
- **Real-World Application**: Ensuring robustness and accuracy in diverse and complex real-world scenarios.

### Clarity is key

It is easy to ask the generative AI to create you an image caption, but with every request the probability that the responses you get differ from each other in various ways are quite high. That is not desirable. Therefore, to face such pitfalls clarity is the key:

- **Creating awareness**: Ask yourself and be aware of the purpose of the captions. Approach it strategically and plan the processes that are associated with the captions. In an ideal world you know about the set of images and its context.
- **Clear instructions**: Clear and unambiguous prompts are essential for generating accurate and consistent image captions. Therefore, use your awareness to provide clear instructions for the generative AI to perform the task. This could as well contain negative prompting techniques.
- **Provide examples**: When providing examples within the instructions, this can help the generative AI to perform a lot better. But, providing examples can also be a pitfall. It makes no sense to provide image caption example of ultrasound images when you like to have image captions for landscape paintings. But, when you expect a variety of different image styles then try to provide this variety within your examples.
- **Validate outputs**: With the use of [Pydantics](https://docs.pydantic.dev/latest/) BaseModel the `ollama-instructor` library is able to support instructions for the generative AI like LLMs (e.g. Llama3, Phi3, Mistral, etc.) or vision models (e.g. LLaVA, moondream, BakLLaVA, etc.) by providing a JSON schema and validate the response based on that JSON schema.
- **Play with temperatures**: Since working with generative AI is mostly a iterating process, above listed tips can be supported by adjusting the temperature within the configurations of the AI. A lower temperature is linked with less variety within the responses, when a higher temperature will lead the AI to be more creative. The most providers ([Ollama included](https://github.com/ollama/ollama/blob/main/docs/modelfile.md#parameter)) support such configurations.


# Captioning images of Pokémons

 [Ollama](https://ollama.com) and its model library provides vision models able to process images for generating descriptive sentences based on the visual content of images in the context of image captioning tasks.
 In the following example, which is using a [dataset on Hugging Face](https://huggingface.co/datasets/svjack/pokemon-blip-captions-en-zh), the approach is to create brief image captions in English and Chinese for a set of Pokémon images. This example shows the use of above listed tips to achieve the desired responses from the LLM with the of Ollama, Pydantic and `ollama-instructor`. For generating the image caption the vision model LLaVA was used.

```Python
from datasets import load_dataset
import rich

ds = load_dataset("svjack/pokemon-blip-captions-en-zh")
ds = ds["train"]

from ollama_instructor.ollama_instructor_client import OllamaInstructorClient

from pydantic import BaseModel, Field
from enum import Enum
from typing import List
import base64
from io import BytesIO

hist = []
for i in range(8):
	hist.append(
		str(
			{"en": ds[i]["en_text"],
			"zh": ds[i]["zh_text"]}
		)
	)
hist_str = "\n".join(hist)
print(hist_str)

def im_to_str(image):
	buffered = BytesIO()
	image.save(buffered, format="JPEG")
	img_str = base64.b64encode(buffered.getvalue())
	return img_str

class Caption(BaseModel):
	en: str = Field(...,
		description="English caption of image",
		max_length=84)
	zh: str = Field(...,
		description="Chinese caption of image",
		max_length=64)

client = OllamaInstructorClient(host='http://localhost:11434', debug=True)

response = client.chat_completion(
	model='llava:13b',
	pydantic_model=Caption,
	allow_partial=True,
	messages=[
		{
			"content": f'''
			You are a highly accurate image to caption transformer.
			Describe the image content in English and Chinese respectly. Make sure to FOCUS on item CATEGORY and COLOR!
			Do NOT provide NAMES! KEEP it SHORT!
			While adhering to the following JSON schema: {Caption.model_json_schema()}
			Following are some samples you should adhere to for style and tone:
			{hist_str}
			''',
			"role": "system"
		}
		,{
			"content": "Describe the image in English and Chinese",
			"role": "user",
			"images": [im_to_str(ds[-1]["image"])]
		}
	],
	options={
		"temperature": 0.25,
	}
)

rich.print(response)
```

In the first part of the code we build the connection and download the dataset. Each image in this dataset already has an image caption in English and Chinese. With the `hist` variable the sample of image captions are stored for having them later in the instruction (prompt).

```Python
hist = []
for i in range(8):
	hist.append(
		str(
			{"en": ds[i]["en_text"],
			"zh": ds[i]["zh_text"]}
		)
	)
hist_str = "\n".join(hist)
print(hist_str)
```
This is how the samples look like:
```JSON
{'en': 'a drawing of a green pokemon with red eyes', 'zh': '红眼睛的绿色小精灵的图画'}
{'en': 'a green and yellow toy with a red nose', 'zh': '黄绿相间的红鼻子玩具'}
{'en': 'a red and white ball with an angry look on its face', 'zh': '一个红白相间的球，脸上带着愤怒的表情'}
{'en': "a cartoon ball with a smile on it's face", 'zh': '笑容满面的卡通球'}
{'en': 'a bunch of balls with faces drawn on them', 'zh': '一堆画着脸的球'}
{'en': 'a cartoon character with a potted plant on his head', 'zh': '一个头上戴着盆栽的卡通人物'}
{'en': 'a drawing of a pokemon stuffed animal', 'zh': '小精灵毛绒玩具的图画'}
{'en': 'a picture of a cartoon character with a sword', 'zh': '一张带剑的卡通人物图片'}
```


Secondly, we have to encode the JPEG into a string and store it in memory, so that the vision model is able to process the image. For this purpose the function `im_to_str` is used:
```Python
def im_to_str(image):
	buffered = BytesIO()
	image.save(buffered, format="JPEG")
	img_str = base64.b64encode(buffered.getvalue())
	return img_str
```

In the next step the Pydantic model gets created to specify the structure of the output. In this specific case, and to avoid a long image caption, we make use of Pydantics `Field` class to restrict the length of the output. In combination with the samples the AI now knows that the length of the caption is limited.
```Python
class Caption(BaseModel):
	en: str = Field(...,
		description="English caption of image",
		max_length=84)
	zh: str = Field(...,
		description="Chinese caption of image",
		max_length=64)
```

And finaly, we set up the instruction in the system prompt by combining it with the image caption samples and the JSON schema of the Pydantic model.
```Python
messages=[
    {
        "content": f'''
        You are a highly accurate image to caption transformer.
        Describe the image content in English and Chinese respectly. Make sure to FOCUS on item CATEGORY and COLOR!
        Do NOT provide NAMES! KEEP it SHORT!
        While adhering to the following JSON schema: {Caption.model_json_schema()}
        Following are some samples you should adhere to for style and tone:
        {hist_str}
        ''',
        "role": "system"
    }
```

The **system** prompt now contains several techniques:
1. Giving the AI a role: "You are a highly accurate image to caption transformer"
2. Describing the output you want: "Describe the image content in English and Chinese respectly.", "While adhering to the following JSON schema: {Caption.model_json_schema()}"
3. Emphasize guidelines: 
	1. Positive: "Make sure to FOCUS on item CATEGORY and COLOR!", "KEEP it SHORT!"
	2. Negative: "Do NOT provide NAMES!"
4. Providing samples of valid responses: "Following are some samples you should adhere to for style and tone: {hist_str}"

To support the consistency of the output and make the AI less creative, the **temperature** can play a highly influencial role, as it was explained above and can be seen in the code example.

Here are some examples of responses:
```
{'en': 'A cartoon crab with a surprised expression', 'zh': '一个惊讶的卡通蟹'}

{'en': 'A cartoon crab with a surprised expression.', 'zh': '一个惊讶的卡通蟹。'}

{'en': 'A cartoon crab with a surprised expression on its face.', 'zh': '一个惊讶的卡通蟹。'}

{'en': 'A cartoon depiction of a red and white Pokémon with a surprised expression.','zh': '一张插图，展示了一只红白相间的小精灵，表情吓人。'}
```


## Using smaller models for image captioning

The same script was executed with a tiny vision model called [Moondream](https://ollama.com/library/moondream) and it was not able to stick to the JSON schema of the Pydantic model and therefore failed most of the times. But this should not be the end and forces us to be more creative in using the tool `ollama-instructor`, but the fundamentals (e.g. prompting techniques) for getting the desired output are the same.

The approach for using smaller vision models or smaller AIs in general could be to build a chain:
1. Instruct the small vision model to provide a the image caption in the needed style
2. Instruct a Large Language Model to response the image caption the the needed schema

```Python
from datasets import load_dataset
import rich

ds = load_dataset("svjack/pokemon-blip-captions-en-zh")
ds = ds["train"]

from ollama_instructor.ollama_instructor_client import OllamaInstructorClient
import ollama
from pydantic import BaseModel, Field
from enum import Enum
from typing import List
import base64
from io import BytesIO

hist_en = []
hist = []
for i in range(8):
	hist.append(
		str(
			{"en": ds[i]["en_text"],
			"zh": ds[i]["zh_text"]}
		)
	)
	hist_en.append(
		str(
			{ds[i]["en_text"]}
		)
	)
hist_str = "\n".join(hist)
hist_en_str = "\n".join(hist_en)
print(hist_str)

def im_to_str(image):
	buffered = BytesIO()
	image.save(buffered, format="JPEG")
	img_str = base64.b64encode(buffered.getvalue())
return img_str

ollama_client = ollama.Client(
	host="http://localhost:11434",
)

vision_response = ollama_client.chat(
	model='moondream:1.8b',
	messages=[
		{
			"role": "system",
			"content": f'''
			You are a highly accurate image to caption transformer.
			Describe the image content in English and Chinese respectly.
			Make sure to FOCUS on item CATEGORY, EXPRESSION, MOTION and COLOR!
			Do NOT provide NAMES! KEEP it SHORT!
			'''
		},
		{
			"content": "Describe the image in English and Chinese",
			"role": "user",
			"images": [im_to_str(ds[-1]["image"])]
		}
	],
	options={
	"temperature": 0.25,
	}
)
rich.print(vision_response['message']['content'])

class Caption(BaseModel):
	en: str = Field(...,
		description="English caption of image",
		max_length=84
	)
	zh: str = Field(...,
		description="Chinese caption of image"
	)

client = OllamaInstructorClient(host='http://localhost:11434', debug=True)

response = client.chat_completion(
	model='qwen2:1.5b-instruct',
	pydantic_model=Caption,
	messages=[
		{
			"content": f'''
			You are a highly accurate algorithm responding in JSON.
			You will get provided a image caption in English. You task is to provide the SHORT VERSION of the image caption and its translation into Chinese.
			Make sure to FOCUS on item CATEGORY, EXPRESSION, MOTION and COLOR!
			While adhering to the following JSON schema: {Caption.model_json_schema()}
			Following are some samples you should adhere to for style and tone:
			{hist_str}
			''',
			"role": "system"
		},
		{
			"content": vision_response['message']['content'],
			"role": "user"
		}
	],
	options={
		"temperature": 0.25,
	}
)

rich.print(response)
```
