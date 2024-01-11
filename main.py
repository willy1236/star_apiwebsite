from fastapi import FastAPI,BackgroundTasks
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
import xml.etree.ElementTree as ET
import os,requests,threading,logging,datetime,time
from dotenv import load_dotenv

load_dotenv()




def create_logger(dir_path,file_log=False,log_level=logging.DEBUG):
	# config
	logging.captureWarnings(True)   # 捕捉 py waring message
	formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
	logger = logging.getLogger('py.warnings')    # 捕捉 py waring message
	logger.setLevel(logging.INFO)

	if file_log:
		filename = datetime.datetime.now().strftime("%Y-%m-%d %H_%M_%S") + '.log'
		# 若不存在目錄則新建
		if not os.path.exists(dir_path):
			os.makedirs(dir_path)

		# file handler
		fileHandler = logging.FileHandler(filename=f"{dir_path}/{filename}",mode='w',encoding='utf-8')
		fileHandler.setFormatter(formatter)
		logger.addHandler(fileHandler)

	# console handler
	consoleHandler = logging.StreamHandler()
	consoleHandler.setLevel(log_level)
	consoleHandler.setFormatter(formatter)
	logger.addHandler(consoleHandler)

	return logger

log = create_logger('./logs',file_log=False,log_level=logging.INFO)
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

@app.route('/discorlinkeddrole')
async def discorlinkeddrole(request:Request):
	params = dict(request.query_params)
	print(params)
	return HTMLResponse('OK')

def run():
    import uvicorn
    uvicorn.run(app,host='0.0.0.0',port=14000)

class ltThread(threading.Thread):
    def __init__(self):
        super().__init__(name='ltThread')
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def run(self):
        while not self._stop_event.is_set():
            log.info("Starting ltThread")
            os.system('lt --port 14000 --subdomain willy1236 --max-sockets 10 --local-host 127.0.0.1 --max-https-sockets 86395')
            #cmd = [ "cmd","/c",'lt', '--port', '14000', '--subdomain', 'willy1236', '--max-sockets', '10', '--local-host', '127.0.0.1', '--max-https-sockets', '86395']
            #cmd = ["cmd","/c","echo", "Hello, World!"]
            #self.process = psutil.Popen(cmd)
            #self.process.wait()
            log.info("Finished ltThread")
            time.sleep(5)

class WebsiteThread(threading.Thread):
    def __init__(self):
        super().__init__(name='WebsiteThread')
        self._stop_event = threading.Event()

    def run(self):
        import uvicorn
        uvicorn.run(app,host='0.0.0.0',port=14000)
        #os.system('uvicorn bot_website:app --port 14000')

if __name__ == '__main__':
    tunnel = ltThread()
    tunnel.start()
    web = WebsiteThread()
    web.start()