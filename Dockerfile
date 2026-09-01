# Retained through cutover as the tested Material rollback. Pinning avoids
# silently changing that rollback path with a floating image tag.
FROM squidfunk/mkdocs-material:9.7.7

# Install additional dependencies
RUN pip install --no-cache-dir mkdocs-macros-plugin==1.5.0

# Set the working directory inside the container
WORKDIR /docs
