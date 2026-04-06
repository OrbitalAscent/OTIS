import pyttsx3

engine = pyttsx3.init()
voices = engine.getProperty('voices')

# Print all available voices to find the British one
for voice in voices:
    print(f"Voice Name: {voice.name}")
    print(f" - ID: {voice.id}")
    print(f" - Languages: {voice.languages}")
    print()

# Once you find the correct ID (e.g., for "Microsoft Hazel Desktop - English (Great Britain)")
# set the voice property with that specific ID.
# Replace 'VOICE_ID_HERE' with the actual ID from the output above
# For example, on some Windows systems, 'Microsoft Hazel' might be the one.

# Example of setting the voice (replace with actual ID)
# engine.setProperty('voice', 'HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\MSTTS_V110_enGB_GeorgeM') 
engine.setProperty('voice', 'HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\MSTTS_V110_enAU_JamesM')
# engine.setProperty('voice', 'HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\MSTTS_V110_enAU_CatherineM') 

engine.say("Hello, I am speaking with a British accent.")
engine.runAndWait()