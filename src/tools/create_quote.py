# from langchain_core.tools import tool
# from pydantic import BaseModel
# from langchain.messages import SystemMessage
# import requests
# from pydantic import BaseModel, EmailStr
# from typing import List


# class PersonalInfo(BaseModel):
#     title: str
#     fastName: str
#     sureName: str
#     email: EmailStr
#     mobleNumber: str
#     postcode: str


# class QuizAnswer(BaseModel):
#     question: str
#     answer: str
#     price: float


# class RequestModel(BaseModel):
#     personalInfo: PersonalInfo
#     quizAnswers: List[QuizAnswer]


# @tool
# def CreateNewQuote(request_model: RequestModel):
#     """"if user completed the quote and user postcode_data then create quote other ways not"
#         and give your code like this 
#         <a href= {https://arronwh-website.vercel.app/boilers/system-selection?quoteId=_id} View your code>
#         Data will collect on this following order and one question at a time them finally fill the postcode_form
#     """
#     url = "https://yeloheatbackend.up.railway.app/api/v1/quote"
#     payload = request_model
#     response = requests.post(url, data=payload)
#     return response