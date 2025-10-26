import cv2
import numpy as np
import matplotlib.pyplot as plt
from mtcnn.mtcnn import MTCNN
from time import time

# ----CARGAR IMAGEN Y DETECCION DE CARAS ---

# Carga imagen (sube archivos en Colab o usa una URL y descárgala)
img = cv2.imread('img2.jpg')  # reemplaza por tu archivo
img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

detector = MTCNN()   # puedes ajustar min_face_size
t0 = time()
res = detector.detect_faces(img_rgb)
t1 = time()

print(f"Detected: {len(res)} rostro(s) • tiempo: {(t1 - t0)*1000:.1f} ms")
for r in res:
    print(r['confidence'], r['box'], r['keypoints'].keys())
    


# # ---- DIBUJAR CAJAS Y LANDMARKS ----
vis = img_rgb.copy()
for r in res:
    x, y, w, h = r['box']
    cv2.rectangle(vis, (x,y), (x+w, y+h), (0,255,0), 2)
    for name, (px,py) in r['keypoints'].items():
        cv2.circle(vis, (px,py), 2, (255,0,0), -1)
plt.imshow(vis); plt.axis('off')
plt.show()


# ---- UMBRALES Y NMS----
detector = MTCNN()  # su NMS interno filtra solapes
# Prueba filtrado por confianza mínima
thr = 0.95
filtrados = [r for r in res if r['confidence'] >= thr]
print(f"Con thr={thr} quedan {len(filtrados)} rostros")


def iou(a, b):
    # a,b en formato [x,y,w,h]
    ax1, ay1, aw, ah = a; ax2, ay2 = ax1+aw, ay1+ah
    bx1, by1, bw, bh = b; bx2, by2 = bx1+bw, by1+bh
    ix1, iy1 = max(ax1,bx1), max(ay1,by1)
    ix2, iy2 = min(ax2,bx2), min(ay2,by2)
    inter = max(0, ix2-ix1)*max(0, iy2-iy1)
    union = aw*ah + bw*bh - inter
    return inter/union if union>0 else 0.0

# Si tienes una caja "ground truth" gt_box, compara:
# print(iou(filtrados[0]['box'], gt_box))

for r in res:
    print(r['box'])


def promedio_ejecucion(cantidad):
    tiempos = []
    for i in range(cantidad):
        t0 = time()
        res = detector.detect_faces(img_rgb)
        t1 = time()
        tiempos.append((t1-t0)*1000)
        print(f"tiempo: {(t1 - t0)*1000:.1f} ms")
    return np.mean(tiempos)

if __name__ == "__main__":
    print(promedio_ejecucion(10))