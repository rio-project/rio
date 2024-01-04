from abc import ABC, abstractmethod, abstractproperty
from typing import Type

from . import article_models


class ArticleBuilder(ABC):
    def __init__(self, title: str, url_segment: str):
        self.title = title
        self.url_segment = url_segment

    @abstractmethod
    def build(self) -> article_models.BuiltArticle:
        raise NotImplementedError()


class ApiDocsArticle(ArticleBuilder):
    def __init__(self, component_class: Type):
        super().__init__(
            component_class.__name__,
            component_class.__name__.lower(),
        )

        self.component_class = component_class

    def build(self) -> article_models.BuiltArticle:
        result = article_models.BuiltArticle()

        result.markdown(
            f"""
# TODO: {self.title}
        """
        )

        return result
