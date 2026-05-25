# from langchain_core.tools import tool
# from pydantic import BaseModel
# from langchain.messages import SystemMessage

# class Body(BaseModel):
#     collection_name: str


# @tool
# def QuizTool():
#     """
#     When user want to get a quotation or quz then they start a quiz. And finally ask about the user information like name, post code, phone number
#     if user one start a quiz then they must need to complete it utill they so stop the quiz.
#     Data will collect on this following order and one question at a time them finally fill the postcode_form"""
    
#     sys_message = SystemMessage(
#         content=""" 
    
# questions_and_options:

# Before starting the quiz:
# - If the user is only exploring boiler types, purchase options, or product choices, do not start the quiz yet.
# - First ask the user to confirm they want to start the quiz/quotation flow.
# - Only begin with serial_no 1 after the user clearly confirms they want to start.

# Questions must come on the following order and sequentially and follow the next also
# Show each question with its serial_no when asking the user.
# Never create, rename, skip, or replace these questions or options.
# When the user confirms with "Start Quiz", ask serial_no 1 exactly:
# "Are you a homeowner or landlord?" with options ["Homeowner", "Landlord"].
#   requirement:
#     serial_no: 1
#     question: "Are you a homeowner or landlord?"
#     options: ["Homeowner", "Landlord"]
#     next:
#       default: fuelType

#   fuelType:
#     serial_no: 2
#     question: "What kind of fuel does your boiler use?"
#     options: ["Gas", "LPG", "Oil"]
#     special:
#       - if: "Oil"
#         action: "redirect"
#         to: "/boilers/callout/oil"
#       - if: "Gas or LPG"
#         next: boilerType

#   boilerType:
#     serial_no: 3
#     question: "Currently, what type of boiler do you have?"
#     options: ["Combi", "Standard", "System", "Back Boiler"]
#     next:
#       Combi: boilerCondition
#       Standard: convertToCombi
#       System: convertToCombi
#       Back Boiler: convertToCombi

#   convertToCombi:
#     serial_no: 4
#     question: "Do you want to convert to a Combi boiler?"
#     options: ["Yes", "No"]
#     special:
#       - if: "boilerType=Back Boiler and convertToCombi=No"
#         action: "redirect"
#         to: "/boilers/callout"
#     next:
#       Yes: boilerCondition
#       No: boilerCondition

#   boilerCondition:
#     serial_no: 5
#     question: "How would you describe your current boiler?"
#     options: ["Not working", "Old & inefficient", "Doesn't fit with our plans", "Other"]
#     next:
#       default: mountedOnWall

#   mountedOnWall:
#     serial_no: 6
#     question: "Is your boiler mounted on the wall?"
#     options: ["Yes it is wall mounted", "No it is floor standing"]
#     next:
#       default: boilerAge

#   boilerAge:
#     serial_no: 7
#     question: "Roughly how old is your boiler?"
#     options: ["Up to 10 years", "10-20 years", "20-25 years", "25+ years", "I don't know"]
#     next:
#       default: stayDuration

#   stayDuration:
#     serial_no: 8
#     question: "How long do you see yourself in your current home?"
#     options: ["Up to 1 years", "1-5 years", "6-10 years", "10+ years", "I don't know"]
#     next:
#       default: waterFlowRate

#   waterFlowRate:
#     serial_no: 9
#     question: "How quickly does your water come out of your cold tap?"
#     options: ["Fast", "Average", "Slow"]
#     special:
#       - if: "Slow"
#         action: "redirect"
#         to: "/boilers/callout"
#     next:
#       Fast: currentBoilerLocation
#       Average: currentBoilerLocation

#   currentBoilerLocation:
#     serial_no: 10
#     question: "Where's your current boiler?"
#     options: ["Utility room", "Kitchen", "Garage", "Airing cupboard", "Other"]
#     special:
#       - if: "Other"
#         action: "show_free_text_prompt"
#         field: "otherRoomName"
#         next: differentPlace
#     next:
#       Utility room: differentPlace
#       Kitchen: differentPlace
#       Garage: differentPlace
#       Airing cupboard: differentPlace

#   differentPlace:
#     serial_no: 11
#     question: "Do you want your new boiler in a different place?"
#     options_by_condition:
#       - if: "currentBoilerLocation=Airing cupboard"
#         options: ["No", "Move somewhere else"]
#       - if: "currentBoilerLocation in [Utility room, Kitchen, Garage, Other]"
#         options: ["No", "Move to airing cupboard", "Move somewhere else"]
#     next:
#       "Move to airing cupboard": airingCupboardLocation
#       "Move somewhere else": newBoilerLocation
#       "No": homeType
#     special:
#       - if: "differentPlace=No and currentBoilerLocation=Airing cupboard"
#         next: airingCupboardLocation

#   airingCupboardLocation:
#     serial_no: 12
#     question: "Where is your airing cupboard?"
#     options: ["Middle of the house", "On an outside wall"]
#     next:
#       default: homeType

#   newBoilerLocation:
#     serial_no: 13
#     question: "Where do you want your new boiler?"
#     options:
#       - "Airing cupboard"
#       - "Utility room"
#       - "Kitchen"
#       - "Garage"
#       - "Bathroom"
#       - "Bedroom"
#       - "Loft or attic"
#       - "Somewhere else"
#     special:
#       - if: "Somewhere else"
#         action: "redirect"
#         to: "/boilers/callout"
#     next:
#       Airing cupboard: airingCupboardLocation
#       Utility room: homeType
#       Kitchen: homeType
#       Garage: homeType
#       Bathroom: homeType
#       Bedroom: homeType
#       "Loft or attic": homeType

#   homeType:
#     serial_no: 14
#     question: "Which of these best describes your home?"
#     options: ["Detached", "Semi Detached", "Terraced", "Flat", "Bungalow"]
#     next:
#       Detached: bedrooms
#       "Semi Detached": bedrooms
#       Terraced: bedrooms
#       Flat: flatOnSecondFloor
#       Bungalow: bungalowFloors

#   bungalowFloors:
#     serial_no: 15
#     question: "Is your bungalow on one or two floors?"
#     options: ["One floor", "Two floors"]
#     next:
#       default: bedrooms

#   flatOnSecondFloor:
#     serial_no: 16
#     question: "Is your flat on or above the second floor?"
#     options: ["Yes", "No"]
#     next:
#       Yes: accessEquipmentCharges
#       No: bedrooms

#   accessEquipmentCharges:
#     serial_no: 17
#     question: "Do you accept that there may be extra charges for access equipment?"
#     options: ["Yes", "No"]
#     special:
#       - if: "No"
#         action: "redirect"
#         to: "/boilers/callout"
#     next:
#       Yes: bedrooms

#   bedrooms:
#     serial_no: 18
#     question: "How many bedrooms do you have?"
#     options: ["1 bedroom", "2 bedrooms", "3 bedrooms", "4 bedrooms", "5 bedrooms", "6+ bedrooms"]
#     next:
#       default: bathtubs

#   bathtubs:
#     serial_no: 19
#     question: "How many bathtubs do you have, or plan to have in the future?"
#     options: ["0 bathtubs", "1 bathtub", "2 bathtubs", "3+ bathtubs"]
#     next:
#       "0 bathtubs": showers
#       "1 bathtub": bathtubShowerOver
#       "2 bathtubs": bathtubShowerOver
#       "3+ bathtubs": bathtubShowerOver

#   bathtubShowerOver:
#     serial_no: 20
#     question: "Do any of your bathtubs have showers over them?"
#     options: ["Yes", "No"]
#     next:
#       default: showers

#   showers:
#     serial_no: 21
#     question: "How many separate showers do you have, or plan to have in the future?"
#     options: ["0 showers", "1 shower", "2+ showers"]
#     next:
#       "0 showers": radiators
#       "1 shower": electricShower
#       "2+ showers": electricShower

#   electricShower:
#     serial_no: 22
#     question: "Do you have an electric shower?"
#     options: ["Yes", "No"]
#     next:
#       Yes: powerShower
#       No: radiators

#   powerShower:
#     serial_no: 23
#     question: "Is it a power shower?"
#     options: ["Yes", "No"]
#     next:
#       Yes: pumpSeparatedFromShower
#       No: radiators

#   pumpSeparatedFromShower:
#     serial_no: 24
#     question: "Is the pump separated from the shower?"
#     options: ["Yes", "No", "I don't know"]
#     next:
#       default: radiators

#   radiators:
#     serial_no: 25
#     question: "How many radiators do you have?"
#     options: ["0-5 radiators", "6-9 radiators", "10-13 radiators", "14-16 radiators", "17+ radiators"]
#     next:
#       default: trv

#   trv:
#     serial_no: 26
#     question: "Do you have Thermostatic Radiator Valves on all your radiators?"
#     options: ["Yes", "No"]
#     next:
#       default: waterMeter

#   waterMeter:
#     serial_no: 27
#     question: "Do you have a water meter?"
#     options: ["Yes", "No"]
#     next:
#       default: flueGroundDistance

#   flueGroundDistance:
#     serial_no: 28
#     question: "How close to the ground is your flue?"
#     options: ["More than 2 metres", "Less than 2 metres"]
#     next:
#       default: fluePropertyDistance

#   fluePropertyDistance:
#     serial_no: 29
#     question: "How close to another property is your flue?"
#     options: ["More than 2 metres", "Less than 2 metres"]
#     next:
#       default: flueUnderStructure

#   flueUnderStructure:
#     serial_no: 30
#     question: "Is the flue under a carport, balcony or other structure?"
#     options: ["Yes", "No"]
#     next:
#       default: flueDoorWindowDistance

#   flueDoorWindowDistance:
#     serial_no: 31
#     question: "Is the flue 30cm or more from a door or window?"
#     options: ["Yes", "No"]
#     next:
#       default: postcode_form

# notes:
#   - "The legacy steps flueOut, roofType, roofPosition, flueWallDistance and flueShape exist only as commented logic and are not part of the active dataset/order."

#     postcode_form:
#     required_fields:
#         - title (Mr/Mrs)
#         - fastName
#         - sureName
#         - email
#         - mobleNumber
#         - postcode(must valid UK post code)
#     submit_payload:
#         - quizAnswers[]: { question, answer, optional price }

#     callout_routes:
#     - "/boilers/callout/oil"
#     - "/boilers/callout"

#     note:
#     - There is dead branch code for flueOut/roofType/roofPosition/flueWallDistance/flueShape in container logic, but those steps are commented out in data and are not active.""")

#     return sys_message.content
