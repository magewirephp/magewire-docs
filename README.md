# Magewire PHP - Documentation

## Installation

To contribute to the documentation, follow these steps:

1. Build Docker image (once or on update):
   ```sh
   docker build -t magewirephp/mkdocs-material .
   ```
   
2. Run locally:
   ```sh
   docker run --rm -it -p 8000:8000 -v ${PWD}:/docs magewirephp/mkdocs-material
   ```
   
3. Visit:
   ```sh
   http://0.0.0.0:8000/magewire-docs/
   ```
