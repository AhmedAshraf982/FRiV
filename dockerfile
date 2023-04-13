FROM continuumio/miniconda3


# Make RUN commands use `bash --login`:
SHELL ["/bin/bash", "--login", "-c"]

# Create the environment
COPY env.yml .
RUN conda env create -f env.yml

# Initialize conda in bash config fiiles:
RUN conda init bash

# Activate the environment, and make sure it's activated:
RUN echo "conda activate myenv-dev" > ~/.bashrc

WORKDIR /server
ADD . /server

# Install dependencies
RUN pip install -r reqs.txt
# Expose port 
ENV PORT 8080

# Run the application:
CMD exec uvicorn server:app --host 0.0.0.0 --port ${PORT} --workers 1