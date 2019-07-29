from time import sleep
import datetime
import requests
import os.path
import json
import os
# --------------------------------------------------------------------------
# Sleep Time for loop
slp = 86400
# set max size for file to download
f_size = 20971520 # bytes - 20MB
# formats able to upload
formats = ["jpg", "png", "csv", "xlsx", "pdf", "doc", "gif"]
# name of cloud preset from Rsync (using owncloud - so "own" for me)
cloud = "own"
# place to save files in cloud - Documents folder for me
dir = "Documents"
# envirment variables - security reasons
api = os.environ.get('API') # Slack API
channel_id = os.environ.get('CHANNEL_ID') # Slack Channel ID
f_time = os.environ.get('F_TIME') # t_time, f_time - Unix Time
t_time = os.environ.get('T_TIME') # start and end time for data-download

# -------------------------------------------------------------------------
def Backupper():
    time = datetime.datetime.now()
    time = time.strftime("%Y/%m/%d - %H:%M")
    print(f'Connected to Slack Server - {time}')
    url = f"https://slack.com/api/files.list?token={api}&channel={channel_id}&ts_from={f_time}&ts_to={t_time}&pretty=1"
    try:
        result = requests.get(url, timeout=8.0)
        if result.ok == True:
            data = json.loads(result.text)
            # Header needed  for file download
            headers = {"Authorization": "Bearer" +
                    f"{api}"}
            count = 0
            for file in data["files"]:
                file_size = int(file["size"])
                file_url = file["url_private_download"]
                file_name = file["name"]
                file_type = str(file["filetype"])
                file_title = file_name
                if file_size > f_size:
                    print(f"File {file_name} is too large to download!")
                    continue
                if file_type not in formats:
                    print("Not allowed format!")
                    continue
                # Chnage file name if same exists
                else:
                    if os.path.exists(file_title):
                        print("""Duplicated file.
                                 Changing name""")
                        count = count + 1
                        file_title = str(count) + file_title
                    response = requests.get(file_url, headers=headers, timeout=8.0)
                    with open(file_title, 'wb') as f:
                        print("Downloading the File: ", file_title)
                        # Save file local
                        f.write(response.content)
                        # Send file to cloud with rclone
                        print("Uploading the file to Cloud: ", file_title)
                        os.system(f"rclone copy --no-traverse --progress {file_title} {cloud}:{dir}") # "--no-traverse" doesn't exists for newer OS (Ubuntu 19)
                        os.system(f"rm -r {file_title}") # Delete file from local storage
    except:
        print ("Wasn't able to connect to Slack!")

# -------------------------------------------------------------------------

if __name__ == '__main__':

    if api == None:
        print(f"API is not set right - {time}")
    elif channel_id == None:
        print(f"ID is not set right - {time}")
    elif f_time == None:
        print(f"start time is not set right - {time}")
    elif t_time == None:
        print(f"end time is not set right - {time}")
    else:
        while True:
            Backupper()
            sleep(slp)
