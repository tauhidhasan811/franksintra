import requests
from langchain_core.tools import tool
from pydantic import BaseModel, EmailStr

class Body(BaseModel):
    referred_by: str
    name: str
    email: EmailStr
    phone: str
    postcode: str
    address: str


@tool
def SaveUserContactInfo(body: Body):
    """
    If user want to contact with customer support, collect their name, email, phone, postcode (valid UK postcode), and address. 
    Save the contact information of the user for contact with our customer support.
    If the information is saved successfully, return a success message. Otherwise, return an error message.
    """

    body.referred_by = "ai"
    url = "https://yeloheatbackend.up.railway.app/api/v1/refer"
    payload = body.model_dump()
    response = requests.post(url, data=payload)
    response = response.json()['success']
    # print(response)
    if response:
        message =  "Your contact information has been saved successfully and our customer support will contact with you very soon."
    else:
        message= "Sorry, there was an error saving your contact information. Please try again later."
    
    # print(message)
    return message
