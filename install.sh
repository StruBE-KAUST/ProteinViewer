git clone
virtualenv -p python3 venv
source venv/bin/activate
pip install --upgrade pip
pip install --upgrade virtualenv
pip install -r requirements.txt
django-admin startproject server_dev
cd server_dev
./manage.py migrate
ln -s ../ProteinViewer/ ./
Edit settings.py : Add ProteinViewer in INSTALLED_APPS
in urls.py, add :
    url(r'viewer/', include('ProteinViewer.urls', namespace="Viewer")),
