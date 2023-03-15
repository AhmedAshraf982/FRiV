FROM python:3.8.16
RUN python -m pip install --upgrade pip

RUN pip install virtualenv
ENV VIRTUAL_ENV=/venv
RUN virtualenv venv -p python3
ENV PATH="VIRTUAL_ENV/bin:$PATH"

WORKDIR /server
ADD . /server

# Install dependencies
RUN pip install -r requirement.txt
# Expose port 
ENV PORT 8080

# Run the application:
CMD exec uvicorn server:app --host 0.0.0.0 --port ${PORT} --workers 1