FROM ubuntu

RUN apt update && apt install python3-pip -y
RUN apt install vim -y
WORKDIR /app

# Copy the requirements.txt file and install Python dependencies
COPY requirements.txt .

RUN pip3 install -r requirements.txt

# Copy the rest of your app's source code from your host to your image filesystem.
COPY . ./app/

CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0"]
