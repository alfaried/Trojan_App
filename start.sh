#!/bin/bash
clear
cd /home/ec2-user/.trojan/trojan_env
. bin/activate
cd Trojan_App/Trojan 
python manage.py runserver 0.0.0.0:8999
