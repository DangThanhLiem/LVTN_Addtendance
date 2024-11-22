import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL': "https://face-recognitionb2014580-default-rtdb.firebaseio.com/",
})

ref = db.reference('Users')

data = {
    "2014580" :
        {
            "name":"Dang Thanh Liem",
            "major":"Developer",
            "total_attendance":6,
            "lever":"Middle",
            "year":"1",
            "starting_year":"2023",
            "last_attendance":"2024-11-6 04:59:00"
        },
    "2014555" :
        {
            "name":"Diana Anna",
            "major":"Tester",
            "total_attendance":7,
            "lever":"Intern",
            "year":"<1",
            "starting_year":"2024",
            "last_attendance":"2024-11-6 05:00:00"
        }
}

for key,value in data.items():
    ref.child(key).set(value)