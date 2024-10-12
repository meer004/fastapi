from fastapi.testclient import TestClient
from fastapi import FastAPI
from dailydo_todo_app import settings
from sqlmodel import SQLModel, create_engine, Session
from dailydo_todo_app.main import app, get_session
import pytest 


#engine is one for whole application
connection_string: str = str(settings.TEST_DATABASE_URL).replace("postgresql", "postgresql+psycopg")
engine = create_engine(connection_string, connect_args={"sslmode":"require"}, 
pool_recycle=300, pool_size=10, echo=True)# engine is been created 
#communicate with database 
#===================================================================
# Refactor with pytest fixture
# 1- arrange, 2- Act, 3- Assert 4 - cleanup
# resorces to perfrm test 1- creating table 2- creating session and overide with test branch
# our client should be created in test branch from test client
# fixer automate arrange and clean up
@pytest.fixture(scope="module",autouse=True)
def get_db_session():
    SQLModel.metadata.create_all(engine)
    yield Session(engine)

# we need to overide dependency get session which came from main we need to overide it 
@pytest.fixture(scope='function') # scope of this fixture is func scope coz every sessin we need session
def test_app(get_db_session):# need app client that's why we give this name / pass 1 fixture in other fixture function
# we need to open session when function starts nd close when function ends
    def test_session():
        yield get_db_session
        app.dependency_overrides[get_session] = test_session
        with TestClient(app=app) as client: # generator function
            yield client



#===================================================================

# test-1: root test
def test_root():
    client = TestClient(app=app) # needs parameter through which t perform testing
    response = client.get('/')
    data = response.json()
    assert response.status_code == 200 # status code is 200 it return true
    assert data == {"message": "wellcome"}
 
 # Test-2: post test / it will post todo n our test branch
def test_create_todo(test_app):
    """ SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        def db_session_override():
            return session
        app.dependency_overrides[get_session] = db_session_override
        client = TestClient(app=app) """
    test_todo = {"content": " create todo test", "is_completed": False}
    response = test_app.post('/todos/', json=test_todo)
    data = response.json()
    assert response.status_code == 200
    assert data["content"] == test_todo["content"]
    


# test - 3 : get all 
def test_get_all(test_app):
    """SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        def db_session_override():
            return session
        app.dependency_overrides[get_session] = db_session_override
        client = TestClient(app=app)"""
    test_todo = {"content": "get all todos test", "is_completed": False}
    response = test_app.post('/todos/', json=test_todo)
    data = response.json()

    response = test_app.get('/todos/')
    new_todo = response.json()[-1]
    assert response.status_code == 200
    assert new_todo["content"] == test_todo["content"]

# Test - 4 : single todo
def test_get_single_todo(test_app):
    """SQLModel.metadata.create_all(engine)# make sure that table is created
    with Session(engine) as session: # creates  a session
        def db_session_override(): # test session override main.py yfunction
            return session
        app.dependency_overrides[get_session] = db_session_override
        client = TestClient(app=app)# create a client"""

    test_todo = {"content": "get single todo test", "is_completed": False}
    response = test_app.post('/todos/', json=test_todo)
    todo_id = response.json()["id"]

    res = test_app.get(f'/todos/ {todo_id} ')
    data = res.json()
    assert res.status_code == 200
    assert data["content"] == test_todo["content"]

# Test - 5 :edited todo
def test_edit_todo(test_app):
    """SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        def db_session_override():
            return session
        app.dependency_overrides[get_session] = db_session_override
        client = TestClient(app=app)"""

    test_todo = {"content": "edit todo test", "is_completed": False}
    response = test_app.post('/todos/',json=test_todo)
    todo_id = response.json()["id"]

    edited_todo = {"content": "we have edited this", "is_completed": False} 
    response = test_app.put(f'/todos/{todo_id} ',json=edited_todo)
    data = response.json()
    assert response.status_code == 200
    assert data["content"] == edited_todo["content"]


# test - 6 : delete todo
def test_delete_todo():
    """SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        def db_session_override():
            return session
        app.dependency_overrides[get_session] = db_session_override
        client = TestClient(app=app)"""

    test_todo = {"content": "delete todo test", "is_completed": False}
    response = test_app.post('/todos/', json=test_todo)
    todo_id = response.json()["id"]

    response = test_app.delete(f'/todos/ {todo_id}')
    data = response.json()
    assert response.status_code == 200
    assert data["message"] == "Task  deleted successfully"