from pydantic import BaseModel

from app.models.enums import Language


class LanguageIn(BaseModel):
    language: Language


class LanguageOut(BaseModel):
    language: Language
