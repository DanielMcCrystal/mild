import re
import json
from functools import lru_cache
import os

HTML_DIR = "html"
CSS_DIR = "css"
DATA_FILENAME = "data.json"
OUTPUT_FILENAME = "resume.html"


def get_data(data_key: str, data):
    fields = data_key.split(".")
    for field in fields:
        data = data[field]
    return data


@lru_cache
def get_raw_html(template_name: str):
    with open(f"{HTML_DIR}/{template_name}.html") as html_f:
        return html_f.read()


def process_data_insert(data_insert: str, data):
    data_key, *args = data_insert.strip("[ ]").split(" ")
    fields = data_key.split(".")
    for field in fields:
        if field not in data:
            print(data)
            raise Exception(f"Invalid data key: {data_key}")
        data = data[field]
    if isinstance(data, list):
        tag = args[0]
        return "".join([f"<{tag}>{item}</{tag}>" for item in data])
    else:
        return data


def process_template_insert(template_insert: str, data):
    template_name, *data_key = template_insert.strip("{ }").split(" ", 1)
    if data_key:
        data_key = data_key[0]
    else:
        data_key = template_name

    data = data.get(data_key, {})
    try:
        return render(get_raw_html(template_name), data)
    except Exception as e:
        raise Exception(f"Error rendering {template_name} with {data_key}: {e}")


def render(template: str, data):
    # Insert all of the data
    html = re.sub(
        r"\[\[.+\]\]", lambda s: process_data_insert(s.group(), data), template
    )
    html = re.sub(
        r"\{\{.+\}\}", lambda s: process_template_insert(s.group(), data), html
    )
    return html


def get_css_files():
    return [f"{CSS_DIR}/{f}" for f in os.listdir(CSS_DIR) if f.endswith(".css")]


def build_html(root_template: str, root_data: dict):
    rendered_body = render(get_raw_html(root_template), data=root_data)
    css_links = "\n".join(
        [f"<link rel='stylesheet' href='{css}'>" for css in get_css_files()]
    )
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        {css_links}
    </head>
    <body>
        {rendered_body}
    </body>
    </html>
    """


with open(f"{DATA_FILENAME}") as data_f:
    root_data = json.load(data_f)
final_html = build_html(root_template="index", root_data=root_data)
with open(OUTPUT_FILENAME, "w") as f:
    f.write(final_html)
