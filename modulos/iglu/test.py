#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import requests

response = requests.get('https://iglu-helados-prod.firebase.io/.json', timeout=300)
print(response.text)

with open("test.josn","w") as variable_name:
    variable_name.write(response.text)