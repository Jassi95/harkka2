#Juho Jääskeläinen 6.3.2022
from xmlrpc.server import SimpleXMLRPCServer
import os
import xml.etree.ElementTree as ET
import datetime
import requests
#Define server and create it
server = SimpleXMLRPCServer(('localhost', 3000),logRequests=True)

#Define functions of the server that can be accessed.
class ApiClass:

    def GET_note(self,topic):#TODO try except
        tree=ET.parse('db.xml')
        root=tree.getroot()
        #Makes wikipedia entry
        data= {'topic':topic}
        data[str(1)]={'note':f'Wikipedia Article About {topic}','text':self._wikiSearh(topic),'timestamp':datetime.datetime.now().strftime("%m/%d/%y - %H:%M:%S")}
        print(data)
        for child in root.findall('topic'):
            #print(child.get('name'))
            if child.get('name').strip().lower()==topic.strip().lower():
                data['topic']=child.get('name')
                i=2
                for note in child.findall('note'):
                    noteName=note.get('name')
                    text= note.find('text').text.strip()
                    timestamp=note.find('timestamp').text.strip()
                    data[str(i)]=(self._parse_to_dict(noteName,text,timestamp))
                    i+=1
                #print(data)
                return data
        return data

    def PUT_note(self,topic,title,text):#TODO try except
        tree=ET.parse('db.xml')
        root=tree.getroot()
        try:
            #Parses the input to xml tree
            topicXML =f"""<topic name="{topic}">
            <note name="{title}">
                <text>
                {text}
                </text>
                <timestamp>
                {datetime.datetime.now().strftime("%m/%d/%y - %H:%M:%S")}
                </timestamp>
            </note>
            </topic>"""

            noteXML=f"""
            <note name="{title}">
                <text>
                {text}
                </text>
                <timestamp>
                {datetime.datetime.now().strftime("%m/%d/%y - %H:%M:%S")}
                </timestamp>
            </note>"""


            for child in root.findall('topic'):#Finds if topic exists

                if child.get('name').strip().lower()==topic.strip().lower(): #If topic found adds new note.
                    print('adding to topic')
                    child.append(ET.fromstring(noteXML))
                    tree.write("db.xml") #writes to database
                    return 201
            #Creates new topic
            print('creating new topic')
            root.append(ET.fromstring(topicXML))
            tree.write("db.xml") #writes to database
        except :
            print('Error invalid input')
            return 400
        return 201



    def _parse_to_dict(self,NoteName,textString,timestampString):#Creates nested dictionary thats close to orginal XML
        data = {'note':NoteName,'text':textString,'timestamp':timestampString}
        #print(data)
        return data

    def _wikiSearh(self,topic):#TODO when adding new topic it looks up link to it in wikipedia!
        S = requests.Session()
        URL = "https://en.wikipedia.org/w/api.php"
        PARAMS = {
            "action": "opensearch",
            "namespace": "0",
            "search": topic,
            "limit": "1",
            "format": "json"
        }

        R = S.get(url=URL, params=PARAMS)
        print('searching wikipedia:')
        DATA = R.json()
        try:
            link = DATA[3][0]
            return link
        except:
            return 'Not found in wikipedia'

        #print(DATA[3][0])
    def _wikiText(self,link):#TODO option to look for data on wikipedia

        return text



#Register functions to the server
server.register_instance(ApiClass())

#Starts the server
if __name__=='__main__':
    try:
        print('Server running...')
        server.serve_forever()
    except KeyboardInterrupt:
        print('Exiting')
