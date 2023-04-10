from typing import List, Optional

from pydantic import BaseModel
from pydantic.main import ModelMetaclass


class AllOptional(ModelMetaclass):
    def __new__(self, name, bases, namespaces, **kwargs):
        annotations = namespaces.get('__annotations__', {})
        for base in bases:
            annotations.update(base.__annotations__)
        for field in annotations:
            if not field.startswith('__'):
                annotations[field] = Optional[annotations[field]]
        namespaces['__annotations__'] = annotations
        return super().__new__(self, name, bases, namespaces, **kwargs)


class Element(BaseModel):
    url: str
    headers: dict
    scrape_type: str
    element_type: str
    element_class: str
    strip_search: str


class ScrapeElement(Element, metaclass=AllOptional):
    pass


class UserTweet(BaseModel):
    id: int
    when: str
    likes: int
    source: str
    content: str


class UserTweets(BaseModel):
    __root__: List[UserTweet]

