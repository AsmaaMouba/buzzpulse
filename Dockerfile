
FROM python:3.8-slim



# Copy the current directory contents into the container at /app
COPY . /app






# Run app.py when the container launches
CMD ["flask", "run"]
HEALTHCHECK CMD curl --fail http://107.20.76.217:8080/ || exit 1

