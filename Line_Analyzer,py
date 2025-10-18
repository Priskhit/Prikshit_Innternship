import os
import math
import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import numpy as np
import cv2
import matplotlib.pyplot as plt

# -----------------------------------------------------------------------------
# Utility math functions
# -----------------------------------------------------------------------------
def length(a, b):
    return math.hypot(b[0] - a[0], b[1] - a[1])

def angle_between(u, v):
    cosA = np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v))
    return math.degrees(math.acos(np.clip(cosA, -1, 1)))

# -----------------------------------------------------------------------------
# 1) Extract only the main figure region via contour masking
# -----------------------------------------------------------------------------
def extract_figure_mask(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Invert so dark lines become white
    _, th = cv2.threshold(gray, 0, 255,
                         cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    # Close small gaps inside the shape
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (31, 31))
    closed = cv2.morphologyEx(th, cv2.MORPH_CLOSE, kernel)
    # Pick the largest external contour
    cnts, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL,
                               cv2.CHAIN_APPROX_SIMPLE)
    if not cnts:
        return np.zeros_like(gray)
    c = max(cnts, key=cv2.contourArea)
    mask = np.zeros_like(gray)
    cv2.drawContours(mask, [c], -1, 255, -1)
    return mask

# -----------------------------------------------------------------------------
# 2) Detect raw straight segments with LSD_REFINE_ADV
# -----------------------------------------------------------------------------
def detect_raw_segments(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    lsd = cv2.createLineSegmentDetector(cv2.LSD_REFINE_ADV)
    res = lsd.detect(gray)
    segs = res[0] if isinstance(res, tuple) else res
    if segs is None:
        return []
    segs = segs.reshape(-1, 1, 4)
    lines = []
    for [[x1, y1, x2, y2]] in segs:
        lines.append(((int(x1), int(y1)), (int(x2), int(y2))))
    return lines

# -----------------------------------------------------------------------------
# 3) Keep only segments whose midpoint lies inside the figure mask and above a minimum length
# -----------------------------------------------------------------------------
def filter_segments(lines, mask, min_len=60):
    h, w = mask.shape
    kept = []
    for A, B in lines:
        if length(A, B) < min_len:
            continue
        mx, my = (A[0] + B[0]) // 2, (A[1] + B[1]) // 2
        if 0 <= mx < w and 0 <= my < h and mask[my, mx] > 0:
            kept.append((A, B))
    return kept

# -----------------------------------------------------------------------------
# 4) Merge perfectly colinear, overlapping segments into full lines
# -----------------------------------------------------------------------------
def merge_colinear(lines, ang_tol=2, dist_tol=15):
    used = [False] * len(lines)
    merged = []
    for i, (A1, B1) in enumerate(lines):
        if used[i]:
            continue
        group = [(A1, B1)]
        theta1 = math.degrees(math.atan2(B1[1]-A1[1], B1[0]-A1[0])) % 180
        for j, (A2, B2) in enumerate(lines[i+1:], start=i+1):
            if used[j]:
                continue
            theta2 = math.degrees(math.atan2(B2[1]-A2[1], B2[0]-A2[0])) % 180
            if abs(theta1 - theta2) < ang_tol or abs(abs(theta1 - theta2) - 180) < ang_tol:
                mid1 = ((A1[0]+B1[0])*0.5, (A1[1]+B1[1])*0.5)
                mid2 = ((A2[0]+B2[0])*0.5, (A2[1]+B2[1])*0.5)
                if length(mid1, mid2) < dist_tol:
                    group.append((A2, B2))
                    used[j] = True
        # merge group endpoints with PCA
        pts = np.array([pt for seg in group for pt in seg])
        mean = pts.mean(axis=0)
        cov = np.cov((pts - mean).T)
        vals, vecs = np.linalg.eig(cov)
        dirv = vecs[:, np.argmax(vals)]
        projs = (pts - mean).dot(dirv)
        p1 = mean + dirv * projs.min()
        p2 = mean + dirv * projs.max()
        merged.append((tuple(p1.astype(int)), tuple(p2.astype(int))))
    return merged

# -----------------------------------------------------------------------------
# 5) Find shared vertices to know which lines meet
# -----------------------------------------------------------------------------
def find_shared_vertices(lines):
    vmap = {}
    for idx, (A, B) in enumerate(lines):
        for pt in (A, B):
            vmap.setdefault(pt, []).append(idx)
    return vmap

# -----------------------------------------------------------------------------
# 6) Compute angles only at those shared vertices
# -----------------------------------------------------------------------------
def compute_angles(lines, vmap):
    angles = []
    for pt, idxs in vmap.items():
        if len(idxs) < 2:
            continue
        A = np.array(pt)
        for i in range(len(idxs)):
            for j in range(i+1, len(idxs)):
                L1, L2 = lines[idxs[i]], lines[idxs[j]]
                B = np.array(L1[1] if L1[0]==pt else L1[0])
                C = np.array(L2[1] if L2[0]==pt else L2[0])
                ang = angle_between(B - A, C - A)
                angles.append((idxs[i], idxs[j], pt, ang))
    return angles

# -----------------------------------------------------------------------------
# 7) Save a UTF-8 report
# -----------------------------------------------------------------------------
def save_report(name, lines, angles):
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = f"{name}_{ts}.txt"
    with open(fname, "w", encoding="utf-8") as f:
        f.write(f"Report for: {name}\nTime: {ts}\n\n")
        f.write(f"Total straight lines: {len(lines)}\n")
        for i, (A, B) in enumerate(lines):
            ori = (math.degrees(math.atan2(B[1]-A[1], B[0]-A[0])) + 360) % 360
            f.write(f"  Line {i}: {A} → {B}, orientation {ori:.1f}°\n")
        f.write("\nAngles at shared vertices:\n")
        for i, j, pt, ang in angles:
            f.write(f"  Lines {i}-{j} at {pt}: {ang:.1f}°\n")
    try:
        os.startfile(fname)
    except:
        messagebox.showinfo("Saved report", fname)

# -----------------------------------------------------------------------------
# 8) Tkinter GUI App
# -----------------------------------------------------------------------------
class App:
    def __init__(self, root):
        self.root = root
        root.title("Figure-Only Straight-Line Analyzer")

        self.img = None
        self.lines = []
        self.angles = []

        ttk.Button(root, text="Upload Figure", command=self.upload) \
            .pack(pady=6)
        self.listbox = tk.Listbox(root, width=70, height=14)
        self.listbox.pack(padx=10, pady=8)
        ttk.Button(root, text="Save & Visualize", command=self.analyze) \
            .pack(pady=6)

    def upload(self):
        path = filedialog.askopenfilename(filetypes=[
            ("Images", "*.png;*.jpg;*.bmp;*.jpeg")])
        if not path:
            return
        self.img = cv2.imread(path)
        name = os.path.splitext(os.path.basename(path))[0]

        # pipeline
        mask   = extract_figure_mask(self.img)
        raw    = detect_raw_segments(self.img)
        filt   = filter_segments(raw, mask)
        merged = merge_colinear(filt)
        vmap   = find_shared_vertices(merged)
        angs   = compute_angles(merged, vmap)

        self.lines  = merged
        self.angles = angs

        # populate GUI
        self.listbox.delete(0, tk.END)
        self.listbox.insert(tk.END, f"Total straight lines: {len(merged)}")
        for i, (A, B) in enumerate(merged):
            ori = (math.degrees(math.atan2(B[1]-A[1], B[0]-A[0])) + 360) % 360
            self.listbox.insert(tk.END, f"L{i}: {A}->{B} @ {ori:.1f}°")
        for i, j, pt, ang in angs:
            self.listbox.insert(tk.END, f"I{i}-{j}@{pt} = {ang:.1f}°")

    def analyze(self):
        if self.img is None or not self.lines:
            return
        save_report("figure", self.lines, self.angles)

        # visualize
        fig, ax = plt.subplots()
        ax.imshow(cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB))
        for A, B in self.lines:
            ax.plot([A[0], B[0]], [A[1], B[1]],
                    color='red', linewidth=2)
        for _, _, pt, ang in self.angles:
            ax.text(pt[0], pt[1], f"{ang:.1f}°",
                    color='yellow', fontsize=12)
        ax.axis('off')
        plt.show()

if __name__ == "__main__":
    import tkinter.ttk as ttk
    root = tk.Tk()
    App(root)
    root.mainloop()
