#!/bin/bash
clear
cd /home/ec2-user/.trojan/trojan_env
. bin/activate
cd Trojan_App
python recovery.py
