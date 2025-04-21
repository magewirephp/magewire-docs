# Magewire PHP - Documentation

## Installation

To contribute to the documentation, follow these steps:

1. Build Docker image (once or on update):
   ```shell
   docker build -t magewirephp/mkdocs-material .
   ```
   
2. Run locally:
   ```shell
   docker run --rm -it -p 8000:8000 -v ${PWD}:/docs magewirephp/mkdocs-material
   ```
   
3. Visit:
   ```shell
   http://0.0.0.0:8000/magewire-docs/
   ```
