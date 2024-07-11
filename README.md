## Install necessary python packages
```
pip install -r requirements.txt
```

## Running Locally

After cloning the repo, put your environmental variables in `.env`.
```
OPENAI_API_KEY = 
UPLOAD_FOLDER =
SERPER_API_KEY =  
STROM_GLASS_API_KEY = 
```

Then, run the following in the command line and your application will be available at `http://localhost:5000`

```bash
python app.py
```
## Running Production mode
pm2 start "gunicorn -w 4 -t 8 -b 0.0.0.0:5000 --timeout 600 app:app"
