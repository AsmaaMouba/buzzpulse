# Use an official lightweight Python image as a parent image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install dependencies from requirements.txt
# Also, add pandas for data manipulation
RUN pip install -r requirements.txt
RUN pip install mysql-connector-python pandas

# Make port 5000 available to the world outside this container
EXPOSE 8080

# Define environment variable
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_DEBUG=True
ENV FLASK_ENV=development
ENV SECRET_KEY=buzz_pulse
ENV CSRF_SECRET_KEY=buzz_pulse
ENV DATABASE_URI=mysql+mysqlconnector://admin:99q&cUzpOG2%@buzzpulse.ccvv7zf7lno9.eu-west-1.rds.amazonaws.com/buzzpulse
ENV THEME=Pulse
ENV MAIL_SERVER=smtp.gmail.com
ENV MAIL_USERNAME=h.in.q.mailing@gmail.com
ENV MAIL_PASSWORD=pmhmjesszshvhauh


# Run app.py when the container launches
CMD ["flask", "run"]
HEALTHCHECK CMD curl --fail http://107.20.76.217:8080/ || exit 1

