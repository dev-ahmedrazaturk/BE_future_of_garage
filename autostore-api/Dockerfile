# Step 1: Use an official Python runtime as a parent image
FROM python:3.9-slim

# Step 2: Set the working directory in the container
WORKDIR /app

# Step 3: Copy the current directory contents into the container
COPY . .

# Step 4: Create and activate a virtual environment inside the container
RUN python -m venv /venv

# Step 5: Install dependencies inside the virtual environment
RUN /venv/bin/pip install --no-cache-dir -r requirements.txt

# # Step 6: Expose the port the app runs on
# EXPOSE 8003

# Step 7: Command to run FastAPI using Uvicorn (with --reload for development)
CMD ["/venv/bin/uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0"]
