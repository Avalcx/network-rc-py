import azure.cognitiveservices.speech as speechsdk
def synthesize_to_speaker():
	#Find your key and resource region under the 'Keys and Endpoint' tab in your Speech resource in Azure Portal
	#Remember to delete the brackets <> when pasting your key and region!
    speech_config = speechsdk.SpeechConfig(subscription="46fb883a118f4f40965f389f418867cf", region="eastasia")
    speech_config.speech_synthesis_language = "zh-CN"
    speech_config.speech_synthesis_voice_name ="zh-CN-XiaoyouNeural"
    #In this sample we are using the default speaker 
    #Learn how to customize your speaker using SSML in Azure Cognitive Services Speech documentation
    audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
    result = synthesizer.speak_text_async("金豆吃屁").get()
    stream = speechsdk.AudioDataStream(result)
    stream.save_to_wav_file("file.wav")
synthesize_to_speaker()