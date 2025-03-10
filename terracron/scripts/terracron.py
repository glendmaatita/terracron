import yaml, hcl2, os
from .models.schedule import Cron

class Terracron:
    def __init__(self, scheduler):
        self.scheduler = scheduler
        self.scheduler_dir_path = os.path.dirname(scheduler)

    def schedule(self):
        cron = self.load_config()

    def load_config(self) -> Cron:
        data = self.open_config()
        cron = Cron(**data)

        for cron in cron.cron:
            for schedule in cron.schedules[:]:
                file_path = os.path.join(os.path.abspath(self.scheduler_dir_path), schedule.file.replace('.', '/')) + ".tf"
                hcl = self.get_hcl_content(file_path)
                hcl_node = self.parse_hcl_node(schedule.node)
                # Set new value
                print(hcl)
                for resource_entry in hcl[hcl_node['resource_type']]:
                    if hcl_node['resource_name'] in resource_entry:  # Ensure resource name exists
                        resource_block = resource_entry[hcl_node['resource_name']]

                        # If resource_id is specified (e.g., 'primary' in 'supabase_project.primary')
                        if hcl_node['resource_id']:
                            if isinstance(resource_block, dict) and hcl_node['resource_id'] in resource_block:
                                
                                if schedule.key in resource_block[hcl_node['resource_id']]:
                                    resource_block[hcl_node['resource_id']][schedule.key] = schedule.value  # Update value

                                else:  # No resource_id (e.g., 'provider' type)
                                    # print(resource_block)
                                    if isinstance(resource_block, dict) and schedule.key in resource_block:
                                        resource_block[schedule.key] = schedule.value  # Update value

                                    elif isinstance(resource_block, list):  # Handle lists of dicts (e.g., required_providers)
                                        for item in resource_block:
                                            if isinstance(item, dict) and schedule.key in item:
                                                item[schedule.key] = schedule.value  # Update value

                print(hcl)
                hcl_output = self.convert_dict_to_hcl(hcl)
                # print(hcl_output)
                # with open(file_path, "w") as f:
                #     f.write(hcl_output)

        return cron
    
    def convert_dict_to_hcl(self, data, indent=0):
        hcl_str = ""
        indent_str = "  " * indent

        for key, value in data.items():
            if isinstance(value, dict):
                hcl_str += f'{indent_str}{key} {{\n{self.convert_dict_to_hcl(value, indent + 1)}{indent_str}}}\n'
            elif isinstance(value, list):
                for item in value:
                    hcl_str += f'{indent_str}{key} {{\n{self.convert_dict_to_hcl(item, indent + 1)}{indent_str}}}\n'
            else:
                hcl_str += f'{indent_str}{key} = "{value}"\n'

        return hcl_str
    
    def get_hcl_content(self, file):
        dict = {}
        with open(file, 'r') as file:
            dict = hcl2.load(file)
        return dict
    
    def parse_hcl_node(self, node):
        parts = node.split(".")
        return {
            "resource_type": parts[0],
            "resource_name": parts[1],
            "resource_id": parts[2]
    }

    # open the configuration file    
    def open_config(self):
        with open(self.scheduler, 'r') as stream:
            try:
                data = yaml.safe_load(stream)
                return data
            except yaml.YAMLError as exc:
                raise ValueError("Failed to load configuration")