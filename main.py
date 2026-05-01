from fastapi import FastAPI,HTTPException,Query
import json

app=FastAPI() 

def load():
    with open('patients.json','r') as f:
        data= json.load(f)

    return data

@app.get("/")
def hello():
    return {'message':'Patient management system API'}

@app.get('/about')
def about():
    return {'message':'A fully functional API to manage to patient records'}

@app.get('/view')
def view():
    data=load()
    return data

@app.get('/patient/{patient_id}')
def view_patient(patient_id:int):
    data=load()
    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404,detail='Patient not found')

@app.get('/sort')
def sort_patients(sort_by:str=Query(...,description='Sort on the basis of hieght, weight or bmi') ,
order:str=Query('asc',description='Sort order, either asc or desc')):

    valid_fields=['height','weight','bmi']
    if sort_by not in valid_fields:
        raise HTTPException(status_code=400,detail='Invalid sort_by parameter')
    if order not in ['asc','desc']:
        raise HTTPException(status_code=400,detail='Invalid order parameter')

    data=load()
    sort_order= True if order=='desc' else False

    sorted_data=sorted(data.values(),key=lambda x:x.get(sort_by,0),reverse=sort_order)
    
    return sorted_data

    
