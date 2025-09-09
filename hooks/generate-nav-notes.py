import logging
import os
from pathlib import Path

import mkdocs.plugins
from mkdocs.config.defaults import MkDocsConfig

log = logging.getLogger(f"mkdocs.plugins.{__name__}")


@mkdocs.plugins.event_priority(100)  # can shoot me in the leg
def on_config(config: MkDocsConfig) -> MkDocsConfig:
    notes_subdir = "nav/pub"
    nav_notes = []
    docs_dir = Path(config["docs_dir"]) / notes_subdir
    assert docs_dir.exists()
    nav_notes = [
        {f"{note.name.strip('.md')}": f"{notes_subdir}/{note.name}"}
        for note in sorted(docs_dir.iterdir(), key=os.path.getctime)
        if "DRAFT" not in note.name
    ]
    config["nav"].append({"Notes": nav_notes})
    return config
