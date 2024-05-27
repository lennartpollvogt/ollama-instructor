from pydantic import BaseModel, Field
from enum import Enum
from typing import List

from ollama_instructor.ollama_instructor_client import OllamaInstructorClient


list_of_enums = {
    'article': 'article',
    'story': 'story',
    'news': 'news',
    'blog': 'blog',
    'comment': 'comment',
    'question': 'question',
    'interview': 'interview'
}

TextTypeEnum = Enum('TextType', list_of_enums)


class TextClassification(BaseModel):
    '''
    This model defines a text classification.
    '''
    title: str = Field(
       ...,
        description="The title of the text.",
    )
    author: str = Field(
       ...,
        description="The author of the text.",
    )
    source: str = Field(
       ...,
        description="The source of the text. For example, the website, magazine or book where the text was published.",
    )
    publishDate: str = Field(
        ...,
        description="The date the text was published. Must be in the format of DD-MM-YYYY.",
    )
    textSummary: str = Field(
       ...,
        description="A brief summary of the text. Should cover the main points of the text.",
        min_length=20,
    )
    TextType: TextTypeEnum = Field(
       ...,
        description="The type of the text. Can be either article, story, news, blog, comment, question, or interview.",
    )
    topics: List[str] = Field(
       default=[],
        description="A list of the topics of the text. For example, the topics of the text can be politics, sports, or technology.",
    )



text: str = '''
publication: 23-01-2022
source: www.example.com
author: Brian The Lamb

# The Fusion of Photography and Fashion: An Artistic Symphony

In the vast and vibrant world of art, the amalgamation of photography and fashion stands out as a dynamic force that transcends time and trends. This artistic symphony not only captures the essence of contemporary culture but also serves as a canvas for creative expression, where every snapshot tells a story, and every outfit is a character in its own right.

## The Birth of Fashion Photography

Fashion photography, as we know it today, emerged in the early 20th century, born out of a necessity to document and advertise the latest clothing designs. However, it quickly evolved from mere catalog images into a form of high art, thanks to visionary photographers who saw the potential in this medium to explore and express ideas of beauty, style, and society.

## A Medium of Endless Creativity

At its core, fashion photography is about storytelling. Through the lens of the photographer, a garment becomes more than just fabric and thread; it transforms into a symbol of identity, culture, and emotion. This genre of photography is unique in its ability to blend elements such as lighting, scenery, and composition with the aesthetic and mood of the clothing, creating images that are not only visually stunning but also rich in narrative.

## The Impact of Technology and Social Media

The advent of digital photography and social media has revolutionized the way we experience fashion photography. High-quality images are now accessible to anyone with a smartphone, democratizing the art form and allowing for a more diverse range of voices and visions to be heard. Social media platforms, in particular, have become virtual galleries for fashion photographers, both amateur and professional, to showcase their work and reach a global audience.

## Challenges and Opportunities

Despite its glamour, fashion photography is not without its challenges. Critics argue that it often perpetuates unrealistic beauty standards and contributes to the commodification of culture. However, many photographers are using their platform to challenge these norms, embracing inclusivity and sustainability in their work. By highlighting diverse bodies, cultures, and fashion practices, they are redefining what fashion photography can be and the messages it can convey.

## The Future of Fashion Photography

As we look to the future, it's clear that fashion photography will continue to evolve, influenced by changes in technology, society, and the fashion industry itself. Virtual and augmented reality, for example, offer new dimensions for creativity, allowing photographers to create immersive experiences that blur the lines between reality and fantasy.

In conclusion, the fusion of photography and fashion is a testament to the power of visual storytelling. It is a field that continues to inspire and be inspired by the changing world around it, forever capturing the beauty, complexity, and dynamism of human expression through fashion. As we move forward, the possibilities are as limitless as the creativity of those who wield the camera.
'''

def test_text_classification(host: str, model: str, **kwargs):
    client = OllamaInstructorClient(
        host=host
    )
        
    response = client.chat_completion(
        model=model,
        pydantic_model=TextClassification,
        messages=[
            {
                'role': 'user',
                'content': 'You task is to classify the following text adhering the provided JSON schema. Your response is an INSTANCE of the JSON schema, so you have to respond in perfect JSON.'
            },
            {
                'role': 'user',
                'content': text
            }
        ],
        **kwargs
    )
    return response