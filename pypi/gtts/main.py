from gtts import gTTS

tts = gTTS('Olá! Este áudio foi gerado com Python.', lang='pt', tld='com.br')
tts.save('mensagem.mp3')