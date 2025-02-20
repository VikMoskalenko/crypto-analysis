FROM python:3.9-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5000
#ENV NAME World
CMD ["python", "app.py"]

## Use official Python image
#FROM python:3.9
#
## Set working directory
#WORKDIR /app
#
## Copy application files
#COPY . .
#
## Install dependencies
#RUN pip install --no-cache-dir -r requirements.txt
#
## Expose the port Flask runs on
#EXPOSE 5000
#
## Start the application
#CMD ["python", "app.py"]

