from pydantic import BaseModel, ConfigDict


class ArkosBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())
