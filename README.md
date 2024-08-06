


# Honeypot SSH Server

A simple SSH honeypot server using Python. The server emulates a fake shell environment to capture and log commands entered by intruders.

## Requirements

- Docker
- Python 3.9


## .env File

```env
HOST=0.0.0.0
PORT=3020
RSA_KEY_FILENAME=honeypot_rsa
LOG_DIR=logs
```


## Running Without Container

1. **Create a Virtual Environment**

   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

2. **Install Dependencies**

   ```sh
   pip install -r requirements.txt
   ```

3. **Run the Server**

   ```sh
   python main.py
   ```

## Running With Container

1. **Build the Docker Image**

   ```sh
   docker build -t honeypot-ssh-server .
   ```

2. **Run the Docker Container**

   ```sh
   docker run -d -p 22:3020 --name honeypot-ssh-server --env-file .env honeypot-ssh-server
   ```

3. **Stopping the Server**

   To stop the server, run:

   ```sh
   docker stop honeypot-ssh-server
   ```

   To remove the container, run:

   ```sh
   docker rm honeypot-ssh-server
   ```




