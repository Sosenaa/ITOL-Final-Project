import pytest
from app import app, get_db_connection, create_tables
import os
from werkzeug.security import generate_password_hash

TEST_DATABASE = "test_task.db"

@pytest.fixture
def client():
     app.config["TESTING"] = True
     app.config["SECRET_KEY"] = "test_secret_key"

     import database
     database.DATABASE = TEST_DATABASE

     with app.app_context():
          create_tables()
     
     with app.test_client() as client:
          yield client

     if os.path.exists(TEST_DATABASE):
          os.remove(TEST_DATABASE)

#Registration test

def test_successfulRegistration(client):
     print("\nTestin: Seccessful registration")
     response = client.post("/register", data={
          "username": "newuser",
          "email": "k.sosnowski1695@gmail.com",
          "password": "Valid123@",
          "confirm_password": "Valid123@"
     }, follow_redirects=True)

     assert response.status_code == 200
     assert b"Registration completed successfully" in response.data
     assert b"Login" in response.data

     print ("--> SUCCESSFUL REGISTRATION. TEST = PASSED")

#login test
def test_successfulLogin(client):
     print("\nTesting: Successful login")
     response = client.post("/register", data={
          "username": "newuser",
          "email": "k.sosnowski1695@gmail.com",
          "password": "Valid123@",
          "confirm_password": "Valid123@"
     }, follow_redirects=True)

     response = client.post("/login", data={
          "username": "newuser",
          "password": "Valid123@",
     }, follow_redirects=True)

     assert response.status_code == 200
     assert b"Login has been successful" in response.data
     assert b"Task Manager" in response.data

     print("--> SECCESSFUL LOGIN TEST = PASSED")
