#!/bin/bash
ip_address=$(dig +short myip.opendns.com @resolver1.opendns.com)
curl "http://$ip_address:8999/event/recovery/send_information/"
