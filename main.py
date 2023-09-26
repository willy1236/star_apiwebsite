from fastapi import FastAPI,BackgroundTasks
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
import xml.etree.ElementTree as ET
import os,requests
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

@app.route('/')
def main(request:Request):
    print(1)
    return HTMLResponse('test')

@app.route('/keep_alive',methods=['GET'])
def keep_alive(request:Request):
    r = HTMLResponse(content='Bot is aLive!')
    return r

@app.route('/osu')
def osu(request:Request):
  params = dict(request.query_params)
  print(params)
  return HTMLResponse('done')

async def get_yt_push(content):
    # tree = ET.parse(content)
    # root = tree.getroot()
    #print(content)
    root = ET.fromstring(content)

    result = {}
    try:
      entry = root.find('{http://www.w3.org/2005/Atom}entry')
      result['id'] = entry.find('{http://www.w3.org/2005/Atom}id').text
      result['videoId'] = entry.find('{http://www.youtube.com/xml/schemas/2015}videoId').text
      result['channelId'] = entry.find('{http://www.youtube.com/xml/schemas/2015}channelId').text
      result['title'] = entry.find('{http://www.w3.org/2005/Atom}title').text
      result['link'] = entry.find('{http://www.w3.org/2005/Atom}link').attrib['href']
      result['author_name'] = entry.find('{http://www.w3.org/2005/Atom}author/{http://www.w3.org/2005/Atom}name').text
      result['author_uri'] = entry.find('{http://www.w3.org/2005/Atom}author/{http://www.w3.org/2005/Atom}uri').text
      result['published'] = entry.find('{http://www.w3.org/2005/Atom}published').text
      result['updated'] = entry.find('{http://www.w3.org/2005/Atom}updated').text
      result['datatype'] = "youtube"
    except Exception as e:
       print(e)
    #print(result)

    url = "https://data.mongodb-api.com/app/data-gzstn/endpoint/data/v1/action/insertOne"
    headers = {
      "Content-Type": "application/json",
      "Access-Control-Request-Headers": "*",
      "api-key": os.getenv("mongodb_api")
    }
    data = {
      "dataSource":"Cluster0",
      "database":"star_database",
      "collection":"api_data",
      "document":result
    }
    requests.post(url,data=data,headers=headers)

@app.get('/youtube_push')
def youtube_push_get(request:Request):
    params = dict(request.query_params)
    if 'hub.challenge' in params:
      return HTMLResponse(content=params['hub.challenge'])  
    else:
        return HTMLResponse('OK')

@app.post('/youtube_push')
async def youtube_push_post(request:Request,background_task: BackgroundTasks):
    body = await request.body().decode('UTF-8')
    background_task.add_task(get_yt_push,body)
    return HTMLResponse('OK')

@app.route('/discordAuth')
async def discordAuth(request:Request):
	params = dict(request.query_params)
	print(params)
	return HTMLResponse('OK')

def run():
    import uvicorn
    uvicorn.run(app,host='0.0.0.0',port=14000)

if __name__ == '__main__':
    run()