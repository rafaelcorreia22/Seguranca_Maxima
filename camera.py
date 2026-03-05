import cv2 
import os
import winsound
import datetime

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Erro ao aceder à câmera.")
    exit()  
else:
    print("Câmera acedida com sucesso.")

# Pasta para salvar os vídeos
os.makedirs("videos", exist_ok=True)

ret, frame1 = cap.read()
if not ret:
    print("Erro ao capturar a frame.")
    cap.release()
    exit()

ret, frame2 = cap.read()
if not ret:
    print("Erro ao capturar a frame.")
    cap.release()
    exit()

# Configurações do vídeo de saída
fourcc = cv2.VideoWriter_fourcc(*'XVID')
fps = 20.0
frame_size = (int(cap.get(3)), int(cap.get(4)))

recording = False
video_writer = None
still_frames = 0
still_frames = 20  # ~1 segundo sem movimento antes de parar de gravar

while cap.isOpened():
    diff = cv2.absdiff(frame1, frame2)
    cv2.imshow("Imagem de diferenca", diff)  # Exibe a imagem de diferença para debug

    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    cv2.imshow("Imagem em escala de cinza", gray)  # Exibe a imagem em escala de cinza para debug

    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    cv2.imshow("Imagem Gaussiana", blur)  # Exibe a imagem borrada para debug

    _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
    cv2.imshow("Imagem a preto e branco", thresh)  # Exibe a imagem de threshold para debug

    eroded = cv2.erode(thresh, None, iterations=3)
    cv2.imshow("Imagem com erosao", eroded)  # Exibe a imagem de threshold para debug

    dilated = cv2.dilate(eroded, None, iterations=5)
    cv2.imshow("Imagem com dilatacao", dilated)  # Exibe a imagem de threshold para debug

    contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    movimento_detectado = False

    for contour in contours:
        if cv2.contourArea(contour) > 2000:
            movimento_detectado = True
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(frame1, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Controle de gravação
    if movimento_detectado:
        print("Movimento detectado!")
        winsound.Beep(1000, 100)

        if not recording:
            # Inicia nova gravação
            nome_arquivo = datetime.datetime.now().strftime("videos/%Y-%m-%d_%H-%M-%S.avi")
            video_writer = cv2.VideoWriter(nome_arquivo, fourcc, fps, frame_size)
            recording = True
            print(f"🔴 recording: {nome_arquivo}")

        still_frames = 0
    else:
        if recording:
            still_frames += 1
            if still_frames > still_frames:
                # Para a gravação
                recording = False
                video_writer.release()
                video_writer = None
                print("🟢 Gravação finalizada.")

    # Salva frame no vídeo se estiver recording
    if recording and video_writer:
        video_writer.write(frame1)

    cv2.imshow("Camera", frame1)

    frame1 = frame2
    ret, frame2 = cap.read()
    if not ret:
        break

    if cv2.waitKey(1) == ord('q'):
        break

# Libera tudo ao sair
if video_writer:
    video_writer.release()

cap.release()
cv2.destroyAllWindows()