import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
import hashlib
import ngrok

class FirebaseAuthentication:
    def __init__(self):
        self.userId = ""
        self.credential_file = "key.json"
        self.listener = None

        cred = credentials.Certificate(self.credential_file)
        # Add both Realtime Database and Storage configurations
        firebase_admin.initialize_app(cred, {
            'databaseURL': "https://desktop-stream-default-rtdb.firebaseio.com",
            'storageBucket': "desktop-stream.appspot.com"
        })

    @staticmethod
    def generate_sha256(input_string):
        sha256 = hashlib.sha256()
        sha256.update(input_string.encode('utf-8'))
        return sha256.hexdigest()

    def is_valid_user(self, userId, passWord):
        self.userId = self.generate_sha256(userId)
        database_path = f"Admin/{self.userId}/password"
        ref = db.reference(database_path)
        data = ref.get()

        if data is not None and passWord == data:
            return True
        return False

    def getKey(self):
        database_path = f"Admin/{self.userId}/key"
        ref = db.reference(database_path)
        data = ref.get()

        if data is not None:
            return data

        return None

    def set_device_status(self, is_active):
        database_path = f"Admin/{self.userId}/is_active"
        ref = db.reference(database_path)
        ref.set(is_active)

    def setLocalhost(self, host):
        database_path = f"Admin/{self.userId}/localhost"
        ref = db.reference(database_path)
        ref.set(host)

    def setHost(self, host):
        database_path = f"Admin/{self.userId}/host"
        ref = db.reference(database_path)
        ref.set(host)

    def setPort(self, port):
        database_path = f"Admin/{self.userId}/port"
        ref = db.reference(database_path)
        ref.set(port)

    def set_ngrok_auth_token(self, token, port):

        try:
            ngrok.set_auth_token(token) 
            self.listener = ngrok.connect(port, "tcp")
            print("Token initialize ", token)
            return True

        except Exception as e:
            print(f"Error setting ngrok auth token: {str(e)}")
            return False

    def connect_ngrok(self):
        try:
            link = self.listener.url().split("://")
            temp = link[1].split(":")
            server_url = temp[0]
            server_port = temp[1]
            print(f"Ingress established at {link}")
            self.setHost(server_url)
            self.setPort(server_port)
        except Exception as e:
            print(e)
        return server_url, server_port

    def disconnect(self):
        ngrok.disconnect(self.listener.url())
        print('ngrok disconnect')

    def upload_file(self, file_name):
        bucket = storage.bucket()

        # Use the original filename as the destination path
        destination_path = "files/" + file_name
        self.setUrl(destination_path)

        #blob = bucket.blob(destination_path)

        #blob.upload_from_filename(file_name)

        # Get the download URL
        #download_url = blob.public_url
        #print(f"File {file_name} available to {download_url}")

        # self.setUrl(download_url)

    def setUrl(self, url):
        database_path = f"Admin/{self.userId}/url"
        ref = db.reference(database_path)
        ref.set(url)




