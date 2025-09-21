# Resonance
### Install
Clone the repo
```
git clone https://github.com/Danny2Forever/Resonance.git
cd Resonance
```
Install Virtual Environment
```
python -m venv .venv
```
Activate environment
```
# for Window
.venv\Scripts\activate

# for MacOS
source .venv/bin/activate
```
Install dependences
```
pip install -r requirements.txt
```
Add .env file
```
DJANGO_SECRET_KEY=your-django-secret-key
SPOTIPY_CLIENT_ID=your-spotify-client-id
SPOTIPY_CLIENT_SECRET=your-client-secret
SPOTIPY_REDIRECT_URI=http://127.0.0.1:8000/callback/
SPOTIFY_SCOPES = "user-read-email user-read-private"

DB_NAME=resonance
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432
```
Migrate
```
python manage.py migrate
```
Try to runserver
```
python manage.py runserver
```
