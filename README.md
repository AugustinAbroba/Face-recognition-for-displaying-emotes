---------- PNGTuber Face Tracking ----------

Um PNGTuber em Python que utiliza visão computacional para rastrear expressões faciais em tempo real e exibir emotes baseados nas emoções detectadas.

======================================

Funcionalidades:

*Captura de webcam em tempo real
*Detecção facial com MediaPipe

*Sistema de emoções:
idle, talk, blink, happy, angry, sad, surprise

*Overlay de imagens PNG com transparência
*Suavização de emoções (buffer)
*Múltiplos modos de visualização:
*Apenas emote (fundo transparente)
*Emote + câmera
*Layout lateral estilo PNGTuber
*Overlay direto no rosto
======================================
Controles
Tecla |	Função
1	| Modo emote transparente
2	| Emote + câmera
3	| Layout PNGTuber
4	| Debug facial
5	| Overlay no rosto
ESC	Sair
======================================
Estrutura esperada
emotes/
├── idle.png
├── talk.png
├── blink.png
├── sad.png
├── angry.png
├── happy.png
└── surprise.png

[Projeto feito utilizando IA]
