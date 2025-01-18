import logging
import os
import re

log = logging.getLogger(f"mkdocs.plugins.{__name__}")

# For Regex, match groups are:
#       0: Whole roamlike link e.g. [[filename#title|alias|widthxheight]]
#       1: Filename e.g. filename.md
#       2: #title
#       3: alias
#       4: width
#       5: height
ROAMLINK_RE = r"""\[\[(.*?)(\#.*?)?(?:\|([\D][^\|\]]+[\d]*))?(?:\|(\d+)(?:x(\d+))?)?\]\]"""

class RoamLinkReplacer:
    def __init__(self, base_docs_url, page_url, attachments_folder):
        self.base_docs_url = base_docs_url
        self.page_url = page_url
        self.attachments_folder = attachments_folder

    def simplify(self, filename):
        """ ignore - _ and space different, replace .md to '' so it will match .md file,
        if you want to link to png, make sure you filename contain suffix .png, same for other files
        but if you want to link to markdown, you don't need suffix .md """
        return re.sub(r"[\-_ ]", "", filename.lower()).replace(".md", "")

    def gfm_anchor(self, title):
        """Convert to gfw title / anchor
        see: https://gist.github.com/asabaylus/3071099#gistcomment-1593627"""
        if title:
            title = title.strip().lower()
            title = re.sub(r'[^\w\u4e00-\u9fff\- ]', "", title)
            title = re.sub(r' +', "-", title)
            return title
        else:
            return ""

    def __call__(self, match):
        # Name of the markdown file
        whole_link = match.group(0)
        filename = match.group(1).strip() if match.group(1) else ""
        title = match.group(2).strip() if match.group(2) else ""
        format_title = self.gfm_anchor(title)
        alias = match.group(3) if match.group(3) else ""
        width = match.group(4) if match.group(4) else ""
        height = match.group(5) if match.group(5) else ""

        # Absolute URL of the linker
        abs_linker_url = os.path.dirname(
            os.path.join(self.base_docs_url, self.page_url))

        # Find directory URL to target link
        rel_link_url = ''
        # Walk through all files in docs directory to find a matching file
        if filename:
            if '/' in filename:
                if 'http' in filename: # http or https
                    rel_link_url = filename
                else:
                    rel_file = filename
                    if not '.' in filename:   # don't have extension type
                        rel_file = filename + ".md"

                    abs_link_url = os.path.dirname(os.path.join(
                        self.base_docs_url, rel_file))
                    # Constructing relative path from the linker to the link
                    rel_link_url = os.path.join(
                            os.path.relpath(abs_link_url, abs_linker_url), os.path.basename(rel_file))
                    if title:
                        rel_link_url = rel_link_url + '#' + format_title
            else:
                attachments_folder = os.path.join(self.base_docs_url, self.attachments_folder)
                for root, dirs, files in os.walk(attachments_folder, followlinks=True):
                    for name in files:
                        # If we have a match, create the relative path from linker to the link
                        if self.simplify(name) == self.simplify(filename):
                            # Absolute path to the file we want to link to
                            abs_link_url = os.path.dirname(os.path.join(
                                root, name))
                            # Constructing relative path from the linker to the link
                            rel_link_url = os.path.join(
                                    os.path.relpath(abs_link_url, abs_linker_url), name)
                            if title:
                                rel_link_url = rel_link_url + '#' + format_title
            if rel_link_url == '':
                log.warning(f"RoamLinksPlugin unable to find {filename} in directory {self.base_docs_url}")
                return whole_link
        else:
            rel_link_url = '#' + format_title

        # Construct the return link
        # Windows escapes "\" unintentionally, and it creates incorrect links, so need to replace with "/"
        rel_link_url = rel_link_url.replace("\\", "/")

        if filename:
            if alias:
                link = f'[{alias}](<{rel_link_url}>)'
            else:
                link = f'[{filename+title}](<{rel_link_url}>)'
        else:
            if alias:
                link = f'[{alias}](<{rel_link_url}>)'
            else:
                link = f'[{title}](<{rel_link_url}>)'

        if width and not height:
            link = f'{link}{{ width="{width}" }}'
        elif not width and height:
            link = f'{link}{{ height="{height}" }}'
        elif width and height:
            link = f'{link}{{ width="{width}"; height="{height}" }}'

        return link


def on_page_markdown(markdown, **kwargs):
    config = kwargs["config"]
    page = kwargs["page"]
    base_docs_url = config["docs_dir"]
    markdown = re.sub(
        ROAMLINK_RE, 
        RoamLinkReplacer(base_docs_url, page.file.src_path, "assets/obsidian_attachments"), 
        markdown
    )
    return markdown