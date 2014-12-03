#!/usr/bin/python2
# -*- coding: utf-8 -*- 
from django.http import HttpResponse
import json

def hello(request):
    resp = {"status": 200,
            "message": "Hello!"
    }
    return HttpResponse(json.dumps(resp), content_type="application/json")
