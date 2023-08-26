from jinja2 import Environment, FileSystemLoader, Template

def make_json_template(template_path:str, template_name:str) -> Template:
    """return jinja2 Template to render ad jsons"""

    env = Environment(loader=FileSystemLoader(template_path))
    template = env.get_template(template_name)
    
    return template