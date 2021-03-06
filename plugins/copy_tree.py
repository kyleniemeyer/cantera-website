"""Copy an entire tree of files.

Replacement plugin for the default Nikola copy_tree plugin.
This plugin copies entire folders at once, rather than individually
copying files within the folder. This substantially reduces the
printed output to stdout during the copying process and is much
faster. We prefer this plugin since we are copying folders around
for the API documentation."""
from shutil import copytree, ignore_patterns, rmtree, copy2
import os

from nikola.plugin_categories import Task
from nikola.utils import config_changed


class CopyTree(Task):
    """Copy an entire tree of files."""

    name = "copy_tree"

    def gen_tasks(self):
        """Copy static files into the output folder."""
        kw = {
            "files_folders": self.site.config["FILES_FOLDERS"],
            "output_folder": self.site.config["OUTPUT_FOLDER"],
        }

        # Ensure this task is created even if nothing needs to be done
        yield self.group_task()

        def copytree_task(src, dst, ignore):
            if os.path.exists(dst):
                rmtree(dst)

            try:
                copytree(src=src, dst=dst, ignore=ignore)
            except NotADirectoryError:
                copy2(src=src, dst=dst)

        for src, rel_dst in kw["files_folders"].items():
            final_dst = os.path.join(kw["output_folder"], rel_dst)
            yield {
                "basename": self.name,
                "name": rel_dst,
                "targets": [final_dst],
                "uptodate": [config_changed(kw, "copy_tree")],
                "actions": [
                    (
                        copytree_task,
                        [],
                        {
                            "src": src,
                            "dst": final_dst,
                            "ignore": ignore_patterns("*.md5", "*.map"),
                        },
                    )
                ],
            }
