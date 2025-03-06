from pydantic import BaseModel
from pydantic.fields import Field
from typing import List

class Git(BaseModel):
    url: str = Field(default=None, title="Git URL")
    directory: str = Field(default=None, title="Directory of Git Repositoy that contains Terraform files")

class Setting(BaseModel):
    git: Git = Field(default=None, title="Git Settings")
    strict: bool = Field(default=None, title="Only run Terraform if there are changes on selected resources")

class Schedule(BaseModel):
    node: str = Field(default=None, title="Node name")
    value: str = Field(default=None, title="Expected value")
    commit: bool = Field(default=None, title="Commit changes to Git repository")

class Resource(BaseModel):
    name: str = Field(default=None, title="Resource name")
    setting: Setting = Field(default=None, title="Resource settings")
    schedule: List[Schedule] = Field(default=None, title="Resource schedules")

class Group(BaseModel):
    resources: List[Resource] = Field(default=None, title="Group resources")