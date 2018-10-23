import ipgetter
import requests as req

def send_signal(public_ip):
    response = {'HTTPStatus':'OK', 'HTTPStatusCode':200}

    try:
        url = "http://52.77.157.29:8000/event/recovery/?secret_key=m0nKEY&ip=" + public_ip #Test server
        #url = "http://cloudtoupus:8000/event/recovery/?secret_key=m0nKEY&ip=" + PUBLIC_IP #Production server
        #print(url)
        resp = req.get(url)
    except:
        response['HTTPStatus'] = 'Bad request'
        response['HTTPStatusCode'] = '400'

    return JsonResponse(response)

if __name__ == '__main__':
    send_signal(ipgetter.myip())
