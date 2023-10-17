import os
import numpy as np
import json
import shutil
import requests
import re as r
from urllib.request import urlopen
from datetime import datetime
from datasets import Image
from PIL import Image
from huggingface_hub import Repository, upload_file

HF_TOKEN = os.environ.get("HF_TOKEN")
DATASET_NAME = "OCR-img-to-text"
DATASET_REPO_URL = "https://huggingface.co/datasets/pragnakalp/OCR-img-to-text"
DATA_FILENAME = "ocr_data.csv"
DATA_FILE = os.path.join("ocr_data", DATA_FILENAME)
DATASET_REPO_ID = "pragnakalp/OCR-img-to-text"
print("is none?", HF_TOKEN is None)
REPOSITORY_DIR = "data"
LOCAL_DIR = 'data_local'
os.makedirs(LOCAL_DIR,exist_ok=True)

try:
    hf_hub_download(
        repo_id=DATASET_REPO_ID,
        filename=DATA_FILENAME,
        cache_dir=DATA_DIRNAME,
        force_filename=DATA_FILENAME
    )
    
except:
    print("file not found")
    
repo = Repository(
    local_dir="ocr_data", clone_from=DATASET_REPO_URL, use_auth_token=HF_TOKEN
)
repo.git_pull()

def getIP():
    ip_address = ''
    try:
    	d = str(urlopen('http://checkip.dyndns.com/')
    			.read())
    
    	return r.compile(r'Address: (\d+\.\d+\.\d+\.\d+)').search(d).group(1)
    except Exception as e:
        print("Error while getting IP address -->",e)
        return ip_address

def get_location(ip_addr):
    location = {}
    try:
        ip=ip_addr
    
        req_data={
            "ip":ip,
            "token":"pkml123"
        }
        url = "https://demos.pragnakalp.com/get-ip-location"
    
        # req_data=json.dumps(req_data)
        # print("req_data",req_data)
        headers = {'Content-Type': 'application/json'}
    
        response = requests.request("POST", url, headers=headers, data=json.dumps(req_data))
        response = response.json()
        print("response======>>",response)
        return response
    except Exception as e:
        print("Error while getting location -->",e)
        return location

"""
Save generated details
"""
def dump_json(thing,file):
    with open(file,'w+',encoding="utf8") as f:
        json.dump(thing,f)

def flag(Method,text_output,input_image):
    
    print("saving data------------------------")
    # try:
    adversarial_number = 0
    adversarial_number = 0 if None else adversarial_number

    ip_address= getIP()
    print("ip_address  :",ip_address)
    location = get_location(ip_address)
    print("location   :",location)
    
    metadata_name = datetime.now().strftime('%Y-%m-%d %H-%M-%S')
    SAVE_FILE_DIR = os.path.join(LOCAL_DIR,metadata_name)
    os.makedirs(SAVE_FILE_DIR,exist_ok=True)
    image_output_filename = os.path.join(SAVE_FILE_DIR,'image.png')
    print("image_output_filename       :",image_output_filename)
    print(input_image)
    try:
        Image.fromarray(input_image).save(image_output_filename)
        # input_image.save(image_output_filename)
    except Exception:
        raise Exception(f"Had issues saving np array image to file")    

    # Write metadata.json to file
    json_file_path = os.path.join(SAVE_FILE_DIR,'metadata.jsonl')
    metadata= {'id':metadata_name,'method':Method,'file_name':'image.png',
                'generated_text':text_output,'ip':ip_address, 'location':location
                }
    
    dump_json(metadata,json_file_path)  
        
    # Simply upload the image file and metadata using the hub's upload_file
    # Upload the image
    repo_image_path = os.path.join(REPOSITORY_DIR,os.path.join(metadata_name,'image.png'))
    
    _ = upload_file(path_or_fileobj = image_output_filename,
                path_in_repo =repo_image_path,
                repo_id=DATASET_REPO_ID,
                repo_type='dataset',
                token=HF_TOKEN
            ) 

    # Upload the metadata
    repo_json_path = os.path.join(REPOSITORY_DIR,os.path.join(metadata_name,'metadata.jsonl'))
    _ = upload_file(path_or_fileobj = json_file_path,
                path_in_repo =repo_json_path,
                repo_id= DATASET_REPO_ID,
                repo_type='dataset',
                token=HF_TOKEN
            )        
    adversarial_number+=1
    repo.git_pull()

    url = 'http://pragnakalpdev35.pythonanywhere.com/HF_space_image_to_text'
    myobj = {'Method': Method,'text_output':text_output,'img':input_image.tolist(),'ip_address':ip_address, 'loc':location}
    x = requests.post(url, json = myobj)
    print("mail status code",x.status_code)
    
    return "*****Logs save successfully!!!!"