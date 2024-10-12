from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import SQLModel, Field, create_engine , Session, select# select table
from dailydo_todo_app  import settings
from typing import Annotated
from contextlib import asynccontextmanager # make context of function



# create model
class Todo(SQLModel, table = True): # model which create data and perform data validation
    id: int | None = Field(default=None, primary_key=True)
    content : str = Field(index=True, min_length=3, max_length=54)
    is_completed :bool =Field(default=False)




#engine is one for whole application
connection_string: str = str(settings.DATABASE_URL).replace("postgresql", "postgresql+psycopg")
engine = create_engine(connection_string, connect_args={"sslmode":"require"}, 
pool_recycle=300, pool_size=10, echo=True)# engine is been created 
#communicate with database for full app ,whole app's communication will bbe handle by engine


# function for table creation
def create_tables(): # whenever app start tables should be created firstly
    SQLModel.metadata.create_all(engine)
    print('creating tables')
    create_tables()
    print("tables created")
    yield # when tables created excution got stop




#for session menagement we make a session function
def get_session():
    with Session(engine) as session:
        yield session # yied function is generator function in python return us session 
 

# make a context/ contextmanager for app coz we want our some of tasks should perform before app startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    print('creating tables')
    create_tables()
    print("tables created")
    yield
    
    
app: FastAPI = FastAPI(
    lifespan=lifespan, title="dailydo todo app", version='1.0.0')

@app.get("/")
async def root():
     return{"message": "wellcome"}


@app.post('/todos/', response_model=Todo)
async def create_todo(todo: Todo, session: Annotated[Session,Depends(get_session)]):
    # dependency injection seperate diferent components of app nd our code will be loosely cupled
    #makes code easy for debuging 
   Session.add(todo)
   Session.commit()
   Session.refresh(todo)
   return todo # return todo will validate from line 53 code response_model=Todo
    

@app.get('/todos/', response_model= list[Todo])
async def get_all(session:Annotated[Session,Depends(get_session)]):#without ge_session it cannot run
    todos = session.exce(select(Todo)).all()
    if todos:
        return todos
    else:
        raise HTTPException(status_code=404, detail="todo not found")

    

@app.get('/todos/{id}' , response_model=Todo)
async def get_single_todo(id:int, session:Annotated[Session, Depends(get_session)]):
    todo = session.exec(select(Todo).where(Todo.id == id)).first()
    if todo:
        return todo
    else:
        raise HTTPException(status_code=404, detail="todo not found")

@app.put('/todos/{id}')
async def edit_todo(id:int,todo:Todo,session:Annotated[Session,Depends(get_session)]):
    existing_todo = session.exec(select(Todo).where(Todo.id == id)).first()
    # single todo came in existing
    if not existing_todo: # if existing todo exist in db make it equal to todo provded by user
        existing_todo.content = todo.content
        existing_todo.is_completed = todo.is_completed
        session.add(existing_todo)
        session.commit()# add data in existing data
        session.refresh(existing_todo) # refresh by adding new data inexisting and return to user
        return existing_todo # changed / modified todo
    else:
        raise HTTPException(status_code=404, detail="todo not found")
        

        
@app.delete('/todos/{id}')
async def delete_todo(id:int, session:Annotated[Session,Depends(get_session)]):
    #todo = session.exec(select(Todo).where(Todo.id == id)).first()
    todo = session.get(Todo, id)
    if todo:
        session.delete(todo)
        session.commit()
        return {"message": "Task  deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="todo not found")

