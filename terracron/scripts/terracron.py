import yaml
from .models.schedule import Schedule

class Terracron:
    def __init__(self, scheduler):
        self.scheduler = scheduler

    def schedule(self):
        schedule = self.load_config()

    def load_config(self) -> Schedule:
        data = self.open_config()
        schedule = Schedule(**data)
        return schedule

    # open the configuration file    
    def open_config(self):
        with open(self.installer, 'r') as stream:
            try:
                data = yaml.safe_load(stream)
                return data
            except yaml.YAMLError as exc:
                raise ValueError("Failed to load configuration")