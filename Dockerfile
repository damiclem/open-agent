# Dockerfile to set up multiple llama.cpp servers for different purposes.
# - Uses debian as base image.
# - Uses slim image as base image, in order to have basic tools available.
# - Sets up three servers at the same time, for different purposes:
#   |-------------------|-------|---------------|---------------|
#   | Model             | Port  | Momory usage  | Scope         | 
#   |-------------------|-------|---------------|---------------|
#   | Nomic Embed V1.5  | 5801  | 100MB         | Embeddings    |
#   | Qwen2.5 Coder     | 5802  | 1.93GB        | Autocomplete  |
#   | Qwen3.5           | 5803  | 5.68GB        | Chat          |
#   |-------------------|-------|---------------|---------------|

# Define base image
FROM debian:bookworm-slim

# Define agen home
RUN mkdir -p /home/agent/

# Define working directory
WORKDIR /home/agent/

# Set user
USER agent

# Execute command
CMD [ "/bin/bash" ]