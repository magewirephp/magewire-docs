FROM squidfunk/mkdocs-material

# Install additional dependencies
RUN pip install mkdocs-macros-plugin

# Set the working directory inside the container
WORKDIR /docs
