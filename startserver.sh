#!/bin/bash
cd /home/ec2-user/coffee-shop/ && pipenv run flask run --reload --host=0.0.0.0 --port=8080