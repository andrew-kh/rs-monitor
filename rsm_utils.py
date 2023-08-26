from jinja2 import Environment, FileSystemLoader, Template

def make_json_template(template_path:str, template_name:str) -> Template:
    """return jinja2 Template to render ad jsons"""

    env = Environment(loader=FileSystemLoader('./meta/'))
    template = env.get_template('oglasi_schema.txt')
    
    return template