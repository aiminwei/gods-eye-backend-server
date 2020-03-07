import requests
import os
import json

pic_directory = "DB/pictures/"

def faceRec(file_name):
    return_response = {'status': None}
    image_path = pic_directory + file_name
    print(image_path)
    image_data = open(image_path, 'rb')
    SUBSCRIPTION_KEY = '8b8cfcd8d7d742b3ba6542827a90fb03'
    ENDPOINT = 'https://testfacial.cognitiveservices.azure.com/face/v1.0/'
    tempfaceid = detectImage(image_data, SUBSCRIPTION_KEY, ENDPOINT)
    if not tempfaceid:
        return_response['status'] = 'Fail'
    else:
        face_id = identifyImage(tempfaceid, SUBSCRIPTION_KEY, ENDPOINT)
        if not face_id:
            return_response['status'] = 'Fail'
        else:
            return_response['status'] = 'Ok'
            return_response['faceId'] = face_id
    return_response = json.dumps(return_response, indent=3)
#    print(return_response)
    return return_response


def detectImage(image_data, subscription_key, endpoint):
    headers = {'Content-Type': 'application/octet-stream',
               'Ocp-Apim-Subscription-Key': subscription_key}
    params = {
        'returnFaceId': 'true',
    }
    response = requests.post(endpoint + 'detect', params=params, headers=headers, data=image_data)
    response.raise_for_status()
    faces = response.json()
    if faces:
        return faces[0]['faceId']
    else:
        return None


def identifyImage(tempfaceid, subscription_key, endpoint):
    headers = {'Content-Type': 'application/json',
               'Ocp-Apim-Subscription-Key': subscription_key}
    params = {
        'personGroupId': 'godseye2020',
        'faceIds': [tempfaceid]
    }
    response = requests.post(endpoint + 'identify', json=params, headers=headers)
    face_id = response.json()
    if face_id:
        return face_id[0]['candidates'][0]['personId']
    else:
        return None