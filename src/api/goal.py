from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from src.api import auth
from src import database as db
import sqlalchemy

router = APIRouter(
    prefix="/goal",
    tags=["goal"],
    dependencies=[Depends(auth.get_api_key)],
)


class Goal(BaseModel):
    goal: str
    type: str
    daily_calories: int

# set goals to goal db with attached user id
@router.post("/{customer_id}")
async def postGoals(goal: Goal, customer_id: int):
    if goal.daily_calories < 1:
        raise HTTPException(status_code=422, detail="Cannot input calorie goal of less than 1")
    
    try:
        with db.engine.begin() as connection:
            sql = """
            INSERT INTO goals (type, goal, customer_id, daily_calories)
            VALUES (:type, :goal, :customer_id, :daily_calories)
            """
            connection.execute(sqlalchemy.text(sql), goal.dict() | {"customer_id": customer_id})
        return "OK"
    
    except:
        print("User already has goal, edit it with PUT request")
        return "Cannot have multiple goals"
    

# Updates goal information
@router.put("/{customer_id}")
async def updateGoal(goal: Goal, customer_id: int):
    if goal.daily_calories < 1:
        raise HTTPException(status_code=422, detail="Cannot input calorie goal of less than 1")
    
    with db.engine.begin() as connection:
        sql = """
        UPDATE goals SET type = :type, goal = :goal, daily_calories = :daily_calories
        WHERE customer_id = :customer_id
        """
        result = connection.execute(sqlalchemy.text(sql), goal.dict() | {"customer_id": customer_id})
    return {"status": "OK", "message" : "Successful update"}