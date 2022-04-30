from io import StringIO
from mjml import mjml_to_html
import requests

def apply_template(dic_library, template_file):
    with open(template_file, "r") as f:
        template = f.read()
        for k,v in dic_library.items():
            template = template.replace(f'{{{{{k}}}}}',str(v))
        return template

def send_admin_report(content, config):
    print(render_mjml_template(content))
    requests.post(
        f"https://api.mailgun.net/v3/{config['mailgun']['domain']}/messages",
        auth=("api", config['mailgun']['apikey']),
        data={
            "from": f"{config['mailgun']['from_name']} <{config['mailgun']['from']}>",
            "to": config['mailgun']['to'],
            "subject": config['mailgun']['subject'],
            "html": render_mjml_template(content)
            })
def render_mjml_template(input):
    return str(mjml_to_html(StringIO(input))).replace('\\n', '')