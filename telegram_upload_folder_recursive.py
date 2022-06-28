#Script will upload all files in a folder recursively to a telegram group
#Requires - api id, api hash, and chat id of group (aka group id)

import telethon
from telethon import TelegramClient
from io import BytesIO
import os
import copy
import sys
import pathlib
from os.path import isfile, isdir, join
from os import listdir
import asyncio
import datetime

api_id = 9 #get the api id
api_hash = 'id' #get the api hash
group_id = -1 # get the group id
dir_p = 'C:' #root directory path where all files and folders that are to be uploaded are present

count = 0
g_entity = None
log_filename = "log.txt"
file_type = "jpg" #Specify file extension to upload only those file types. To upload all file types, keep this as "ALL"
max_async_queue = 5 #Maximum number of files that will be uploaded concurrently
async def get_g_entity(client, group_id):
    global g_entity
    g_entity = await client.get_input_entity(group_id)

async def recursive_call_to_upload_in_folder(dir_path, client):
    lis = listdir(dir_path)
    tasks = []

    for l in lis:
        f_name = join(dir_path, l)
        if isdir(f_name):
            await recursive_call_to_upload_in_folder(f_name, client)
        elif isfile(f_name) and (f_name.split(".")[-1] == file_type or file_type == "ALL"):
            f = open(log_filename, "r")
            f_logs = str(f.read())
            f.close()
            if l in f_logs or f_name in f_logs:
                continue
            global count
            count += 1
            try:
                tasks.append(client.send_file(g_entity, f_name, force_document=True, caption=str(count) + " " + str(dir_path)))
                f = open(log_filename, "a")
                f.write("Queued: " + f_name + "\n")
                f.close()
                print("Queue successful")
            except Exception as e:
                f = open(log_filename, "a")
                f.write("Queue failed : " + f_name + "\n" + str(e) + "\n")
                f.close()
                print("Queue failure")
            if not count%max_async_queue:
                for future in asyncio.as_completed(tasks):
                    f = open(log_filename, "a")
                    try:
                        try:
                            name = future.cr_frame.f_locals
                        except:
                            name = ""
                        await future
                        f = open(log_filename, "a")
                        f.write("Task finished : " + str(name)  + str(datetime.datetime.now()) + "\n")
                        f.close()
                        print("Upload successful")
                    except Exception as e:
                        f.write("Task failed : " + str(name) + "\n" + str(e) + "\n")
                        print("Upload failure")
                    f.close()
                tasks = []
    if tasks:
        for future in asyncio.as_completed(tasks):
            f = open(log_filename, "a")
            try:
                try:
                    name = future.cr_frame.f_locals
                except:
                    name = ""
                await future
                f = open(log_filename, "a")
                f.write("Task finished : " + str(name)  + str(datetime.datetime.now()) + "\n")
                print("Upload successful")
            except Exception as e:
                f.write("Task failed : " + str(name) + "\n" + str(e) + "\n")
                print("Upload failure")
            f.close()
    f = open(log_filename, "a")
    f.write("\n Done Folder: " + dir_path + "\n")
    f.close()

client = TelegramClient('session_id',
    api_id=api_id, api_hash=api_hash,
    # proxy=(socks.PROXY_TYPE_HTTP, 'server', 3128)
)
print("Client about to start")
client.start()
print("Client start successful")

print("Fetching group entity")
loop = asyncio.get_event_loop()
loop.run_until_complete(get_g_entity(client, group_id))

print("Starting recursive call")

loop = asyncio.get_event_loop()
loop.run_until_complete(recursive_call_to_upload_in_folder(dir_p, client))
