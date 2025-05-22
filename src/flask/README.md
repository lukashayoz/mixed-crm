# Getting started
```
# Activate virtualenv
source .venv/bin/activate

# Install dependencies 
pip install -r requirements.txt

# Initialize the database
flask --app flaskr init-db

# Run the app
flask --app flaskr run

# Debug the app
flask --app flaskr run --debug
```

# Use Docker
```
# Build the image
docker build -t mixed-crm .

# Run the container
docker run -p 5000:5000 mixed-crm
```
