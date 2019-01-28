#!/bin/bash
cd "$(dirname "$0")"

while read -r prefix val; do
    case "$prefix" in
        FW:) fw=$val ;;
        Name:) name=$val ;;
        Temperature:) temp=$val ;;
        Moisture:) mt=$val ;;
        Light:) lt=$val ;;
        Conductivity:) ct=$val ;;
        Battery:) bt=$val ;;
    esac
done < <(sudo python3 demo.py --backend bluepy poll $1)

#moisture
curl "http://localhost:8080/json.htm?type=command&param=udevice&idx=$2&nvalue=0&svalue=$mt&battery=$bt"

#temperature
curl "http://localhost:8080/json.htm?type=command&param=udevice&idx=$3&nvalue=0&svalue=$temp&battery=$bt"

#light
curl "http://localhost:8080/json.htm?type=command&param=udevice&idx=$4&svalue=$lt&battery=$bt"

#conductivity
curl "http://localhost:8080/json.htm?type=command&param=udevice&idx=$5&nvalue=0&svalue=$ct&battery=$bt"
