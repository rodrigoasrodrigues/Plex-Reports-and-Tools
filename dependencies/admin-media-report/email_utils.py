from io import StringIO
from mjml import mjml_to_html
import requests

def apply_template(dic_library, template_file):
    with open(template_file, "r") as f:
        template = f.read()
        template = apply_grouploop(dic_library, template)
        for k, v in dic_library.items():
            template = template.replace(f'{{{{{k}}}}}',str(v))
        return template


def apply_grouploop(dic_library, template):
    if not '{{begin.grouploop}}' in template:
        return template
    template_pre = template.split('{{begin.grouploop}}')[0]
    template_pos = template.split('{{begin.grouploop}}')[1]
    template_line = template_pos.split('{{end.grouploop}}')[0]
    template_pos = template_pos.split('{{end.grouploop}}')[1]
    groups = dic_library['metric_groups']
    line_results = ""
    for group in groups:
        line = template_line.replace('{{metric_key}}',f'<b>{str(group)}</b>')
        line = line.replace('{{metric_val}}','')
        line = line.replace('{{metric_percent}}','')
        line_results += line
        for group_item in dic_library[group]:
            line = template_line.replace('{{metric_key}}',str(group_item))
            line = line.replace('{{metric_val}}',str(dic_library[group_item]))
            line = line.replace('{{metric_percent}}',str(dic_library[f'{group_item}_percent']))
            line_results += line
    return template_pre + line_results + template_pos

def send_admin_report(content, config):
    # print(render_mjml_template(content))
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