from vosk import Model, KaldiRecognizer #download from website then cmd: pip install vosk
import pyaudio
import keyboard
import ollama #download from website then cmd: pip install ollama
import pyttsx3 #cmd: pip install datetime
import pyodbc #cmd: pip install datetime
import numpy as np #cmd: pip install datetime
import datetime #cmd: pip install datetime
import re #Regular Expression
import serial #cmd: pip install pyserial
import time

#SQL SERVER==============================================================================
connection = pyodbc.connect(
     "DRIVER={SQL SERVER};"
     "SERVER=DESKTOP-H528BHI\\SQLEXPRESS;"
     "DATABASE=OTIS;"
     "Trusted_Connection=yes;"
)
cursor = connection.cursor()

#SERIAL PORT=============================================================================
ser = serial.Serial(
     port='COM7',
     baudrate=9600,
     timeout=0
)
time.sleep(1)#arduino needs a second to wake up

#SPEECH TO TEXT==========================================================================
model = Model(r"C:\Users\OTIS\Desktop\O.T.I.S\vosk-model-en-us-0.42-gigaspeech")
recognizer = KaldiRecognizer(model,48000)
mic = pyaudio.PyAudio()
for i in range(mic.get_device_count()):#list all available audio devices
    dev = mic.get_device_info_by_index(i)
    if dev['name'] == "Microphone (TONOR G11 USB micro":
        stream = mic.open(format=pyaudio.paInt16, channels=dev['maxInputChannels'], rate=48000, input_device_index=i, input=True,frames_per_buffer=8192)
        print("Microphone found")
        break
        # print((i,dev['name'],dev['maxInputChannels']))
stream.start_stream()
isListening = True

#TEXT TO SPEECH==========================================================================
engine = pyttsx3.init()
engine.startLoop(False)
engine.setProperty('voice', 'HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\MSTTS_V110_enAU_JamesM')

#CREATE EMBEDDING========================================================================
def embed(text: str) -> bytes:
    response = ollama.embeddings(
        model="nomic-embed-text", #cmd: ollama pull nomic-embed-text 
        prompt=text 
    )
    vec = np.array(response["embedding"], dtype=np.float32)
    return vec.tobytes()

#ADD MEMORY==============================================================================
def add_memory(resp: str, userInput: str, type: str = "general"):
     content =f"""User: {userInput}
     Assistant: {resp}"""
     
     embedded_bytes = embed(content)

     query = """
          INSERT INTO Memory (Content, Embedding, Type, DateCreated)
          VALUES (?,?,?,?)
          """
     cursor.execute(query,content,embedded_bytes,type,datetime.datetime.now(datetime.UTC))
     connection.commit()

def check_class(response: str) -> str:
     return re.findall(r'<(\w+)>',response)

def check_command(response: str) -> str:
     return re.findall(r'\*(\w+)\*',response)

def bytes_to_vector(b: bytes):
     return np.frombuffer(b, dtype=np.float32)

def cosine_similarity(a, b):
     return np.dot(a, b)/(np.linalg.norm(a) * np.linalg.norm(b))

def get_memory(user_input: str, top_k: int = 5):
     input_embedding = embed(user_input)
     input_vector = bytes_to_vector(input_embedding)

     cursor.execute("SELECT TOP 10 Content, Embedding, Type FROM Memory")
     results = cursor.fetchall()

     scored_memories = []

     for row in results:
          content = row.Content
          embedding = row.Embedding

          memory_vector = bytes_to_vector(embedding)

          score = cosine_similarity(input_vector, memory_vector)

          scored_memories.append((content,score))
     
     scored_memories.sort(key=lambda x: x[1], reverse=True)

     return[m[0] for m in scored_memories[:top_k]]

def execute_command(command):
     for x in command:
          if x == 'lightsoff':
               ser.write(str.encode("one_off"))
          elif x == 'lightson':
               ser.write(str.encode("one_on"))




#LOOP====================================================================================
print("STT: Now Listening")
while isListening:
     if keyboard.is_pressed('q'):
         print("STT: Quitting")
         isListening = False
         engine.endLoop()
         break

     data = stream.read(4096, exception_on_overflow= False)

     if recognizer.AcceptWaveform(data):
          text = recognizer.Result()
          

          if text[14:-3] != "":
               memories = get_memory(text[14:-3], top_k=5)
               memory_block = "\n".join(f"- {m}" for m in memories)

               prompt = f"""
               You are a helpful home assistant named OTIS that has known the user for a while. 
               Answer like a british butler and the user is your employer.
               Keep your responses concise and short.

               You can execute commands by using the following syntax in your response: *command_name*. 
               Only use these commands when relevant to the conversation. If the user asks you to do 
               something you do not have a command for reply with "I do not have that functionality yet".
               Here is the list of commands you can execute and what they do: 
               *lightson* - turns on the lights, 
               *lightsoff* - turns on the lights, 
               *time* - use this to insert the current time into your response when requested, 
               *weather* - use this to inser the current weather into your response

               At the end of every single response choose a classification from the 
               below list of classifications. Put a < symbol before the chosen classification word from below
               and a > after. Only respond with the chosen classification. Do not put the word 
               classification or <classification> before it. Always include a classification. 
               Label any questions about time as conversation.
               Example: <fact>. Here is the list of classifications:
               <fact> - Objective truths about the user or world, 
               <userfact> -A fact about the user,
               <identity> - Stable info about the user, 
               <preference> - How the user likes responses, 
               <conversation> - Short-term non-important chat context,
               <task> - What the user is trying to do right now,
               <command> - The user asked you to do something,
               <assitantfact> - a fact about you the assistant,
               <problem> - Current issue or blocker

               Relevant memory:
               {memory_block}

               Use this memory if it is helpful, but do not mention it explicitly.

               User: {text[14:-3]}
               Assistant:
               """  

               print("User: " + text[14:-3])
               res = ollama.chat(
                    model='llama3:8b',
                    options={
                         "num_gpu": 99,
                         "num_thread": 4,
                         "num_predict": 150, # cap max output tokens — don't let it ramble
                    },
                    messages=[
                         {'role': 'user',
                         'content': prompt}
                    ]
                    # ,keep_alive=True
               )
               # print(prompt)
               response = res['message']['content']
               print(response)
               classify = check_class(response)
               command = check_command(response)
               
               response_no_class = response
               for x in classify: #remove class
                    response_no_class = response_no_class.replace("<" + x + ">","")
               response_no_class_command = response_no_class
               for y in command:#remove class and commands
                    #execute the command
                    response_no_class_command = response_no_class_command.replace("*" + y + "*","")
               if command:
                    execute_command(command)
                    
               engine.say(response_no_class_command)
               engine.iterate()
               while engine.isBusy():
                    engine.iterate()
               if len(classify) > 0:
                    chosen_class = ""
                    #sometimes it still puts <classification> before the chosen classification word
                    if classify[0] == "classification" and len(classify)>1:
                         chosen_class = check_class(response)[1]
                    else:
                         chosen_class = check_class(response)[0]
                    add_memory(response,text[14:-3],chosen_class)