import yaml, hcl2, os, subprocess, sys, datetime
from .models.schedule import Cron

class Terracron:
    def __init__(self, scheduler):
        self.scheduler = scheduler
        self.scheduler_dir_path = os.path.dirname(scheduler)

    def schedule(self):
        cron = self.load_config()

        # write to tf files
        self.prepare_tf_files(cron)

        # run terraform init
        self.run_terraform_init()

        # run terraform apply autoapprove
        for cron in cron.cron:
            if not cron.setting.strict:
                self.run_terraform_apply_autoapprove()
            else:
                self.run_terraform_plan()

    def run_terraform_init(self) -> bool:
        cmd = "terraform init"
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1, universal_newlines=True)
        for line in process.stdout:
            print(line, end="")
            sys.stdout.flush()
        process.wait()
        return True
    
    def run_terraform_apply_autoapprove(self) -> bool:
        cmd = "terraform apply -auto-approve"
        return self.run_command(cmd)
    
    def run_terraform_plan(self) -> bool:
        cmd = "terraform plan"
        return self.run_command(cmd)
    
    def run_terraform_(self) -> bool:
        cmd = "terraform apply -auto-approve"
        return self.run_command(cmd)

    def git_commit(self, file_path, branch):
        cmd = f"git add {file_path}"
        self.run_command(cmd)
        cmd = f"git commit -m 'Scheduled commit at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'"
        self.run_command(cmd)
        cmd = f"git push origin {branch}"
        self.run_command(cmd)

    def git_reset(self):
        cmd = "git reset --hard"
        self.run_command(cmd)
    
    def run_command(self, cmd):
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1, universal_newlines=True)
        for line in process.stdout:
            print(line, end="")
            sys.stdout.flush()
        process.wait()
        return True
    
    def prepare_tf_files(self, cron):
        for cron in cron.cron:
            for schedule in cron.schedules[:]:
                file_path = os.path.join(os.path.abspath(self.scheduler_dir_path), schedule.file.replace('.', '/')) + ".tf"
                hcl = self.get_hcl_content(file_path)
                hcl_node = self.parse_hcl_node(schedule.node)
                
                # Set new value
                for resource_entry in hcl[hcl_node['resource_type']]:
                    if hcl_node['resource_name'] in resource_entry: 
                        resource_block = resource_entry[hcl_node['resource_name']]

                        if hcl_node['resource_id']:
                            if isinstance(resource_block, dict) and hcl_node['resource_id'] in resource_block:
                                
                                if schedule.key in resource_block[hcl_node['resource_id']]:
                                    resource_block[hcl_node['resource_id']][schedule.key] = schedule.value
                                else:
                                    if isinstance(resource_block, dict) and schedule.key in resource_block:
                                        resource_block[schedule.key] = schedule.value

                                    elif isinstance(resource_block, list):  # Handle lists of dicts (e.g., required_providers)
                                        for item in resource_block:
                                            if isinstance(item, dict) and schedule.key in item:
                                                item[schedule.key] = schedule.value

                hcl_output = self.convert_dict_to_hcl(hcl)
                with open(file_path, "w") as f:
                    f.write(hcl_output)

    def load_config(self) -> Cron:
        data = self.open_config()
        cron = Cron(**data)
        return cron
    
    def convert_dict_to_hcl(self, data, indent=0):
        hcl_str = ""
        indent_str = "  " * indent

        for key, value in data.items():
            if key == "resource" and isinstance(value, list):  
                # Handle resource blocks
                for resource in value:
                    for resource_type, instances in resource.items():
                        for instance_name, instance_values in instances.items():
                            hcl_str += f'resource "{resource_type}" "{instance_name}" {{\n'
                            hcl_str += self.convert_dict_to_hcl(instance_values, indent + 1)
                            hcl_str += "}\n\n"
            elif key == "provider" and isinstance(value, list):  
                for provider_value in value:
                    for provider_name, provider_values in provider_value.items():
                        hcl_str += f'provider "{provider_name}" {{\n'
                        hcl_str += self.convert_dict_to_hcl(provider_values, indent + 1)
                        hcl_str += "}\n\n"
            elif key == "terraform" and isinstance(value, list):
                hcl_str += f"terraform {{\n"
                for tf_value in value:
                    for sub_key, sub_value in tf_value.items():
                        if sub_key == "backend" and isinstance(sub_value, list):
                            for bv in sub_value:
                                for backend_type, backend_values in bv.items():
                                    hcl_str += f'  backend "{backend_type}" {{\n'
                                    hcl_str += self.convert_dict_to_hcl(backend_values, indent + 2)
                                    hcl_str += "  }\n"
                        elif sub_key == "required_providers" and isinstance(sub_value, list):
                            hcl_str += "  required_providers {\n"
                            for bv in sub_value:
                                for provider_name, provider_values in bv.items():
                                    hcl_str += f'    {provider_name} = {{\n'
                                    hcl_str += self.convert_dict_to_hcl(provider_values, indent + 3)
                                    hcl_str += "    }\n"
                                hcl_str += "  }\n"
                        else:
                            hcl_str += f'  {sub_key} {{\n'
                            hcl_str += self.convert_dict_to_hcl(sub_value, indent + 2)
                            hcl_str += "  }\n"
                hcl_str += "}\n\n"
            elif isinstance(value, dict):
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