import os
import markdown

from .settings import ServerSettingsManager
settings = ServerSettingsManager.get_instance().settings

class Command:
    description = "Copy's the root project README.md to the server assets folder."
    
    def __init__(self, manager, parser):
        self.manager = manager

    def run(self, args, configuration):
        self.args = args
        self.configuration = configuration

        doc_md = ""
        with open(os.path.join(settings.PROJECT_DIR, 'README.md'), 'r') as f:
            doc_md = f.read()

        doc_html = markdown.markdown(doc_md)

        with open(os.path.join(settings.PROJECT_DIR, 'server/templates/_docs_md.html'), 'w') as f:
            f.write(doc_html)

        print("Updated documentation HTML based on README.md")
