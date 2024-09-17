FROM rayproject/ray:latest

# Set working directory
WORKDIR /app

# Copy the entire app directory
COPY ./app /app

# Install dependencies from requirements.txt
COPY ./app/requirements.txt /app/

RUN pip install --no-cache-dir -r /app/requirements.txt

