from fastapi import FastAPI,Path, HTTPException,Query 
from fastapi.responses import JSONResponse
from pydantic import BaseModel,Field,computed_field
from typing import Annotated,Literal,Optional
app = FastAPI()
class Patient(BaseModel):
    id:Annotated[str,Field(..., description='id of the pateint',examples=['P001'])]
    name:Annotated[str,Field(..., description='Name of the patient')]
    city:Annotated[str,Field(..., description='city in which the patient lives')]
    age:Annotated[int,Field(..., gt=0,lt=120 ,description='Age of the patient')]
    gender:Annotated[Literal['male','female','others'], Field(..., description='gender of the patient')]
    height:Annotated[float,Field(..., description='height of the patient')]
    weight:Annotated[float, Field(..., description='weight of the patient')]


class PatientUpdate(BaseModel):
    name:Annotated[Optional[str],Field(default=None)]
city:Annotated[Optional[str],Field(default=None)]
age:Annotated[Optional[int],Field(default=None)]
gender:Annotated[Optional[Literal['male','female','others']], Field(default=None)]
height:Annotated[Optional[float],Field(..., description='height of the patient')]
weight:Annotated[Optional[float], Field(deault=None)]




@computed_field
@property
def bmi(self) -> float:
        bmi=round(self.weight/(self.height**2),2)
        return bmi

        
    

@computed_field
@property
def verdict(self) ->str:

       if self.bmi<18.5:
           return 'UNDERWEIGHT'
       elif self.bmi<25:
           return 'NORMAL'
       elif self.bmi<30:
           return 'NORMAL'
       else:
           return 'OBESE'
       


@app.get("/")
def root():
    return{'message':'patient management systen API'}
    


@app.get("/about")
def about():
    return{'message':'YAHA IMANDARI CHALELA BABU'}    
import json


def load_data():
    with open('patient.json','r') as f:
        data = json.load(f)
        return data
    

def save_data(data):
    with open('patient.json', 'w') as f:
        json.dump(data,f)

@app.get('/view')    
def view():
    data= load_data()
    return data

@app.get("/patient/{patient_id}")
def view_patient(patient_id:str=Path(..., description='id of the patient in the database', example='P001')):
    data =load_data()
    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404, detail="patient not found")

@app.get('/sort')
def sort_patients(sort_by: str= Query(..., description='sort on the basis of height,weight,bmi'), order: str=Query('asc',description='sort in the ascending or descending order')):
    valid_inputs=['height','weight','bmi']
    if sort_by not in valid_inputs:
        raise HTTPException(status_code=404, detail='select from valid_inputs{valid_inputs}')
    if order not in ['asc','des']:
        raise HTTPException(status_code=400, detail='invalid input select from asc and des')
    data=load_data()
    sort_order=True if order=='des' else False
    sorted_data=sorted(data.values(),key=lambda x: x.get(sort_by,0), reverse=sort_order)
    return sorted_data


     
@app.post('/create')
def create_patient(patient:Patient):

    data=load_data()

    #check if patient is already present

    if patient.id in data :
        raise HTTPException(status_code=201,detail='Patient already present')
    
    
    #new patient addition into the database
    data[patient.id]=patient.model_dump(exclude=['id'])
    
    #save into the json file
    save_data(data)

    return JSONResponse(status_code=201, content={'patient added to the database'})
 


@app.put('/edit/{patient_id}')
def update_patient(patient_id:str, patient_update:PatientUpdate):
    data =load_data()
    if patient_id not in data:
        raise HTTPException(status_code=404,detail='patient not found')
    existing_patient_info=data[patient_id]
    updated_partient_info=patient_update.model_dump(exclude_unset=True)

    for key,value in  updated_partient_info.items():
        existing_patient_info[key]=value



    existing_patient_info['id']=patient_id
    patient_pydantic_obj=Patient(**existing_patient_info)
    existing_patient_info=patient_pydantic_obj.model_dump(exclude='id')

    data[patient_id]=existing_patient_info

    save_data(data)
    
    return JSONResponse(status_code=200,content={'message':'patient updated'})

@app.delete('/delete/{patient_id}')
def delete_patient(patient_id:str):
    data=load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404,detail="patient not found")
    
    del data[patient_id]

    save_data(data)
    return JSONResponse(status_code=200,content={'message':'patient deleted'})

