# Use a Miniconda base image
# 'continuumio/miniconda3:latest' is a common and stable choice.
# You could also use 'mambaorg/micromamba:latest' for a smaller image and faster builds if you're familiar with micromamba.
FROM continuumio/miniconda3:latest

# Set the working directory inside the container.
# This is where your application code will reside.
WORKDIR /app

# Copy the environment.yml file into the container.
# This file is crucial for recreating your conda environment.
COPY environment.yml .

# Create the conda environment from the environment.yml file.
# The 'name:' field in your environment.yml will define the name of the created environment.
# '-y' flag automatically answers yes to prompts.
# This step can take a while as it downloads and installs all packages.
RUN conda env create -f environment.yml -y

# Copy your entire project directory into the container.
# This includes your run.py file and any other necessary scripts/modules.
COPY . .

# Specify the command to run when the container starts.
# 'conda run -n your_environment_name' is the recommended and most robust way to execute
# commands within a specific conda environment in a Docker container.
# It handles activating the environment for the command you provide.

# IMPORTANT: Replace 'your_environment_name' below with the EXACT name
# specified in the 'name:' field of your 'environment.yml' file.
CMD ["conda", "run", "-n", "condaenv", "python", "run.py"]

# Optional: Expose ports if your run.py runs a web server (e.g., FastAPI, Flask)
# If run.py serves a web application, you'll need to expose the port.
# For example, if your app runs on port 8000:
# EXPOSE 8000

