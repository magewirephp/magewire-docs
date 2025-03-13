def define_env(env):
    """Hook function to define macros and variables."""

    # Retrieve nested variable from mkdocs.yml -> extra.includes.dir
    includes_dir = env.conf['extra'].get('includes', {}).get('dir', 'includes')

    def include(file, **kwargs):
        """Reads a Markdown file and replaces placeholders with parameters."""
        import os

        file_path = os.path.join(includes_dir, file)

        if not os.path.exists(file_path):
            return f"!!! danger \"File \"{file}\" not found.\""

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        for key, value in kwargs.items():
            content = content.replace(f"{{{{ {key} }}}}", str(value))

        return content

    env.variables['include'] = include
