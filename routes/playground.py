
import json
from flask import Blueprint, jsonify, request
from utils.decorators import error_handler
from routes.timelines import generate_ai_timeline
from utils.timelines import process_ai_events
playground_bp = Blueprint('playground', __name__)
from models.user import User
import config as c


events = [
    {
      "name": "Roman London founded",
      "startDate": "43",
      "description": "The Romans establish the city of London as a major settlement."
    },
    {
      "name": "Great Fire of London",
      "startDate": "1666-09-02",
      "endDate": "1666-09-06",
      "description": "A devastating fire that swept through the city, destroying much of the medieval London."
    },
    {
      "name": "The Blitz",
      "startDate": "1940-09-07",
      "endDate": "1941-05-11",
      "description": "A sustained bombing campaign by Nazi Germany during World War II that targeted London."
    },
    {
      "name": "The Black Death",
      "startDate": "1348",
      "description": "The bubonic plague devastates London, killing a large portion of the population."
    },
    {
      "name": "The Great Plague",
      "startDate": "1665",
      "description": "Another outbreak of the bubonic plague in London, leading to many deaths."
    },
    {
      "name": "The Peasants' Revolt",
      "startDate": "1381-06-13",
      "description": "A major uprising in medieval England, culminating in a march on London."
    },
    {
      "name": "The English Civil War",
      "startDate": "1642-08-22",
      "endDate": "1651-09-03",
      "description": "A series of armed conflicts and political machinations between Parliamentarians and Royalists."
    },
    {
      "name": "The Industrial Revolution",
      "startDate": "18th century",
      "description": "A period of major industrialization and innovation that transformed London into a modern city."
    },
    {
      "name": "London Olympics",
      "startDate": "2012-07-27",
      "endDate": "2012-08-12",
      "description": "The city hosts the Summer Olympic Games, showcasing its cultural and sporting heritage."
    },
    {
      "name": "Brexit Referendum",
      "startDate": "2016-06-23",
      "description": "The United Kingdom votes to leave the European Union, impacting London's status as a global financial hub."
    }
  ]


@playground_bp.route("/playground/", endpoint="test", methods=['POST'])
@error_handler
def playground():
    global events

    User(uid='0Gu3S71O2Thq0bSv5DTY7pszf1P2')
    # timeline = generate_ai_timeline(request.json['timelineName'], request.json['nEvents'], request.json['lang'])
    events = process_ai_events(events)
    print(events)

    return jsonify('coucou'), 200