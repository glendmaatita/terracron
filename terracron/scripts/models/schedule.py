from pydantic import BaseModel
from pydantic.fields import Field
from typing import List

class Git(BaseModel):
    url: str = Field(default=None, title="Git URL")
    directory: str = Field(default=None, title="Directory of Git Repositoy that contains Terraform files")

class Setting(BaseModel):
    git: Git = Field(default=None, title="Git Settings")
    branch: str = Field(default=None, title="Git branch")
    strict: bool = Field(default=None, title="Only run Terraform if there are changes on selected resources")

class Schedule(BaseModel):
    file: str = Field(default=None, title="Terraform file")
    node: str = Field(default=None, title="Node name")
    key: str = Field(default=None, title="Key name")
    value: str = Field(default=None, title="Expected value")
    commit: bool = Field(default=None, title="Commit changes to Git repository")

class Resource(BaseModel):
    name: str = Field(default=None, title="Resource name")
    setting: Setting = Field(default=None, title="Resource settings")
    schedules: List[Schedule] = Field(default=None, title="Resource schedules")

class Cron(BaseModel):
    cron: List[Resource] = Field(default=None, title="Schedule resources")