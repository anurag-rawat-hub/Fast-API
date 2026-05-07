from fastapi import FastAPI,HTTPException,Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal, Optional
import json

app=FastAPI() 

class Patient(BaseModel):
    id:Annotated[str, Field(..., description='ID of the patient', examples=['P001'])]
    name:Annotated[str, Field(..., description='Name of the patient', )]
    city:Annotated[str, Field(..., description='City of residence of the patient', )]
    age:Annotated[int, Field(..., description='Age of the patient', gt=0,lt=120)]
    gender:Annotated[Literal['Male','Female','Other'], Field(..., description='Gender of the patient', )]   
    height:Annotated[float, Field(..., description='Height of the patient in m', gt=0)]
    weight:Annotated[float, Field(..., description='Weight of the patient in kg', gt=0)]


    @computed_field
    @property 
    def bmi(self) -> float:
        bmi=self.weight / (self.height ** 2)
        return bmi

    @computed_field
    @property
    def verdict(self) -> str:
        if self.bmi < 18.5:
            return 'Underweight'
        elif self.bmi < 25:
            return 'Normal weight'
        elif self.bmi < 30:
            return 'Normal'
        else:
            return 'Obese'

class PatientUpdate(BaseModel):
    name:Annotated[Optional[str], Field(default=None)]
    city:Annotated[Optional[str], Field(default=None)]
    age:Annotated[Optional[int], Field(default=None,gt=0)]
    gender:Annotated[Optional[Literal['Male','Female','Other']], Field(default=None)]
    height:Annotated[Optional[float], Field(default=None, gt=0)]
    weight:Annotated[Optional[float], Field(default=None,gt=0)]


def load():
    with open('patients.json','r') as f:
        data= json.load(f)

    return data

def save(data):
    with open('patients.json','w') as f:
        json.dump(data,f)

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


@app.post('/create')
def create_patient(patient:Patient):

    #load existing data
    data=load()

    #check if the patient already exists
    if patient.id in data:
        raise HTTPException(status_code=400,detail='Patient with this ID already exists')
    
    #new patient add to the datatbase
    data[patient.id]=patient.model_dump(exclude=['id'])

    #save into the json file
    save(data)

    return JSONResponse(status_code=201, content={'message': 'Patient created successfully'})
    

@app.put('/edit/{patient_id}')
def update_patient(patient_id:str, patient_update:PatientUpdate):
    data=load()

    if patient_id not in data:
        raise HTTPException(status_code=404,detail='Patient not found')

    existing_patient=data[patient_id]

    updated_patient=patient_update.model_dump(exclude_unset=True)

    for key, value in updated_patient.items():
        existing_patient[key]=value
    
    existing_patient['id']=patient_id
    patient_pydantic_obj=Patient(**existing_patient)
    existing_patient=patient_pydantic_obj.model_dump(exclude='id')

    data[patient_id]=existing_patient

    save(data)
    return JSONResponse(status_code=200, content={'message':'patient updated'})


@app.delete('/delete/{patient_id}')
