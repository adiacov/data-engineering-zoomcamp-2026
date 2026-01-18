FROM python:3.13-slim

# set application directory
WORKDIR /app

# create virtual environment inside the image
RUN python -m venv .venv

# make .venv the default python
ENV PATH="./venv/bin:$PATH"

# copy project source
COPY pipeline/ /app/

# install project and dependencies
RUN pip install --no-cache-dir .

# default command
CMD ["python", "pipeline.py"]