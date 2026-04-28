"""Generate architecture and ER diagrams for the diploma thesis."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import matplotlib.patheffects as pe
import numpy as np

OUT = "/Users/thanatos/Documents/school/Final project/thesis_images"

# ─────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────
def rounded_box(ax, x, y, w, h, label, sublabel=None,
                fc="#ffffff", ec="#2c3e50", lw=1.5,
                fontsize=10, bold=False, radius=0.04):
    box = FancyBboxPatch((x - w/2, y - h/2), w, h,
                         boxstyle=f"round,pad=0,rounding_size={radius}",
                         facecolor=fc, edgecolor=ec, linewidth=lw, zorder=3)
    ax.add_patch(box)
    weight = "bold" if bold else "normal"
    va = "center" if sublabel is None else "top"
    dy = 0 if sublabel is None else h * 0.15
    ax.text(x, y + dy, label, ha="center", va=va,
            fontsize=fontsize, fontweight=weight, zorder=4, color="#1a1a2e")
    if sublabel:
        ax.text(x, y - h * 0.1, sublabel, ha="center", va="center",
                fontsize=fontsize - 1.5, color="#555555", zorder=4, style="italic")

def arrow(ax, x1, y1, x2, y2, label="", color="#2c3e50", bidirectional=False):
    style = "<->" if bidirectional else "->"
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle=style, color=color,
                                lw=1.5, connectionstyle="arc3,rad=0.0"),
                zorder=2)
    if label:
        mx, my = (x1+x2)/2, (y1+y2)/2
        ax.text(mx, my + 0.08, label, ha="center", va="bottom",
                fontsize=7.5, color=color, zorder=5,
                bbox=dict(fc="white", ec="none", pad=1))


# ─────────────────────────────────────────────────────────
# 1. ARCHITECTURE DIAGRAM
# ─────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(14, 9))
ax.set_xlim(0, 14)
ax.set_ylim(0, 9)
ax.axis("off")
fig.patch.set_facecolor("#f4f6f9")
ax.set_facecolor("#f4f6f9")

# Title
ax.text(7, 8.6, "Архитектура на системата за сигурност",
        ha="center", va="center", fontsize=14, fontweight="bold", color="#1a1a2e")

# ── Raspberry Pi 5 boundary ──────────────────────────────
pi_box = FancyBboxPatch((0.3, 0.3), 13.4, 7.7,
                        boxstyle="round,pad=0,rounding_size=0.1",
                        facecolor="#eaf4fb", edgecolor="#2980b9",
                        linewidth=2, linestyle="--", zorder=1)
ax.add_patch(pi_box)
ax.text(0.65, 7.75, "Raspberry Pi 5", fontsize=8.5, color="#2980b9",
        fontweight="bold", va="center", zorder=4)

# ── Web Browser ──────────────────────────────────────────
rounded_box(ax, 2.2, 6.5, 2.6, 1.0, "Уеб браузър",
            "Bootstrap 5.3 / HTML", fc="#fef9e7", ec="#f39c12", lw=2, bold=True)

# ── Flask Web App ────────────────────────────────────────
# outer frame
flask_frame = FancyBboxPatch((4.4, 4.0), 5.4, 4.2,
                             boxstyle="round,pad=0,rounding_size=0.07",
                             facecolor="#eafaf1", edgecolor="#27ae60",
                             linewidth=2, zorder=2)
ax.add_patch(flask_frame)
ax.text(7.1, 8.0, "Flask уеб приложение", ha="center", fontsize=9.5,
        fontweight="bold", color="#27ae60", zorder=4)

# inner Flask components
rounded_box(ax, 5.5, 7.1, 1.6, 0.7, "auth_bp", "/auth routes",
            fc="#d5f5e3", ec="#27ae60", fontsize=8)
rounded_box(ax, 7.2, 7.1, 1.6, 0.7, "main_bp", "protected routes",
            fc="#d5f5e3", ec="#27ae60", fontsize=8)
rounded_box(ax, 8.9, 7.1, 0.8, 0.7, "config.py", None,
            fc="#d5f5e3", ec="#27ae60", fontsize=7)

rounded_box(ax, 5.5, 6.0, 1.6, 0.7, "models.py", "SQLAlchemy ORM",
            fc="#d5f5e3", ec="#27ae60", fontsize=8)
rounded_box(ax, 7.2, 6.0, 1.6, 0.7, "extensions.py", "db / login_mgr",
            fc="#d5f5e3", ec="#27ae60", fontsize=8)
rounded_box(ax, 8.9, 6.0, 0.8, 0.7, "Jinja2\nTemplates", None,
            fc="#d5f5e3", ec="#27ae60", fontsize=7)

rounded_box(ax, 5.5, 4.8, 1.6, 0.75, "camera.py", "MJPEG singleton",
            fc="#d5f5e3", ec="#27ae60", fontsize=7.5)
rounded_box(ax, 7.2, 4.8, 1.9, 0.75, "face_recognition\n_listener.py", None,
            fc="#d5f5e3", ec="#27ae60", fontsize=7)
rounded_box(ax, 9.0, 4.8, 0.7, 0.75, "keypad\n_listener",
            None, fc="#d5f5e3", ec="#27ae60", fontsize=7)

# ── MySQL Database ───────────────────────────────────────
rounded_box(ax, 7.1, 2.5, 3.0, 1.2, "MySQL база данни",
            "security_system", fc="#fdf2f8", ec="#8e44ad", lw=2, bold=True)

# ── Hardware modules ─────────────────────────────────────
rounded_box(ax, 1.6, 2.5, 2.2, 1.0, "USB камера",
            "OpenCV / face_recognition", fc="#fef5e7", ec="#e67e22", lw=1.8)
rounded_box(ax, 4.3, 2.5, 2.0, 1.0, "Матричен keypad",
            "4×3, GPIO (BCM)", fc="#fef5e7", ec="#e67e22", lw=1.8)
rounded_box(ax, 1.6, 1.0, 2.2, 1.0, "Пръстов отпечатък",
            "AS608, UART /dev/ttyAMA0", fc="#fef5e7", ec="#e67e22", lw=1.8)
rounded_box(ax, 4.3, 1.0, 2.0, 1.0, "Врати (GPIO реле)",
            "is_locked toggle", fc="#fef5e7", ec="#e67e22", lw=1.8)

# ── Arrows ───────────────────────────────────────────────
# Browser ↔ Flask
arrow(ax, 3.5, 6.5, 4.4, 6.5, "HTTP / HTTPS", color="#2c3e50", bidirectional=True)

# Flask → MySQL
arrow(ax, 7.1, 4.0, 7.1, 3.1, "SQLAlchemy", color="#8e44ad")

# Flask → Camera
arrow(ax, 5.2, 4.4, 2.7, 3.0, "get_frame()", color="#e67e22")
# Flask → Keypad
arrow(ax, 6.7, 4.4, 4.8, 3.0, "GPIO polling", color="#e67e22")
# Flask → Fingerprint
arrow(ax, 5.2, 4.4, 2.1, 1.5, "UART enroll/delete", color="#e67e22")
# Flask → Door relay
arrow(ax, 6.7, 4.4, 4.8, 1.5, "is_locked toggle", color="#e67e22")

# Legend
legend_items = [
    mpatches.Patch(fc="#eafaf1", ec="#27ae60", label="Flask App"),
    mpatches.Patch(fc="#fdf2f8", ec="#8e44ad", label="MySQL БД"),
    mpatches.Patch(fc="#fef9e7", ec="#f39c12", label="Уеб браузър"),
    mpatches.Patch(fc="#fef5e7", ec="#e67e22", label="Хардуер (Pi)"),
]
ax.legend(handles=legend_items, loc="lower right", fontsize=8,
          framealpha=0.9, edgecolor="#aaa", fancybox=True)

plt.tight_layout()
plt.savefig(f"{OUT}/arhitektura.png", dpi=180, bbox_inches="tight",
            facecolor=fig.get_facecolor())
plt.close()
print("✓ arhitektura.png saved")


# ─────────────────────────────────────────────────────────
# 2. ER DIAGRAM
# ─────────────────────────────────────────────────────────
COLORS = {
    "main":     ("#dce8f5", "#2471a3"),   # users, doors
    "cred":     ("#d5f5e3", "#1e8449"),   # pin_codes, fingerprints, face_encodings
    "junction": ("#fef9e7", "#b7950b"),   # junction tables
    "log":      ("#fdf2f8", "#7d3c98"),   # access_logs
}

def er_table(ax, x, y, title, fields, color_key="main", w=2.8):
    fc, ec = COLORS[color_key]
    row_h = 0.28
    header_h = 0.38
    total_h = header_h + len(fields) * row_h + 0.08

    # Header
    header = FancyBboxPatch((x, y - header_h), w, header_h,
                            boxstyle="round,pad=0,rounding_size=0.04",
                            facecolor=ec, edgecolor=ec, linewidth=0, zorder=3)
    ax.add_patch(header)
    ax.text(x + w/2, y - header_h/2, title, ha="center", va="center",
            fontsize=8, fontweight="bold", color="white", zorder=4)

    # Body
    body = FancyBboxPatch((x, y - total_h), w, total_h - header_h,
                         boxstyle="round,pad=0,rounding_size=0.0",
                         facecolor=fc, edgecolor=ec, linewidth=1.2, zorder=3)
    ax.add_patch(body)

    for i, (fname, ftype, is_pk, is_fk) in enumerate(fields):
        fy = y - header_h - (i + 0.5) * row_h
        prefix = "[PK] " if is_pk else ("[FK] " if is_fk else "     ")
        color = "#c0392b" if is_pk else ("#2471a3" if is_fk else "#333333")
        ax.text(x + 0.12, fy, f"{prefix}{fname}", ha="left", va="center",
                fontsize=6.5, color=color, fontweight="bold" if is_pk else "normal", zorder=4)
        ax.text(x + w - 0.08, fy, ftype, ha="right", va="center",
                fontsize=5.8, color="#777777", zorder=4)
        if i < len(fields) - 1:
            ax.plot([x + 0.05, x + w - 0.05],
                    [fy - row_h/2, fy - row_h/2],
                    color="#cccccc", lw=0.5, zorder=4)

    # return center-left and center-right connector points
    cy = y - total_h/2
    return (x, cy), (x + w, cy), (x + w/2, y), (x + w/2, y - total_h)

def er_arrow(ax, p1, p2, label="", one_many=True):
    x1, y1 = p1
    x2, y2 = p2
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="->" if one_many else "-",
                                color="#555555", lw=1.1,
                                connectionstyle="arc3,rad=0.0"),
                zorder=2)
    if label:
        mx, my = (x1+x2)/2, (y1+y2)/2
        ax.text(mx, my + 0.07, label, ha="center", va="bottom",
                fontsize=5.5, color="#555", zorder=5,
                bbox=dict(fc="white", ec="none", pad=0.5))


fig2, ax2 = plt.subplots(figsize=(16, 11))
ax2.set_xlim(0, 16)
ax2.set_ylim(0, 11)
ax2.axis("off")
fig2.patch.set_facecolor("#f7f9fc")
ax2.set_facecolor("#f7f9fc")

ax2.text(8, 10.65, "ER диаграма — База данни: security_system",
         ha="center", va="center", fontsize=14, fontweight="bold", color="#1a1a2e")

# ── Table definitions ─────────────────────────────────────
W = 2.9  # default table width

# users  (top-center)
u = er_table(ax2, 6.2, 10.0, "users", [
    ("id",           "INT PK",     True,  False),
    ("name",         "VARCHAR(120)",False, False),
    ("username",     "VARCHAR(80)", False, False),
    ("email",        "VARCHAR(200)",False, False),
    ("password_hash","VARCHAR(256)",False, False),
    ("role",         "VARCHAR(40)", False, False),
    ("is_active",    "BOOLEAN",    False, False),
    ("last_login",   "DATETIME",   False, False),
], "main", w=W)

# doors (right side)
d = er_table(ax2, 12.5, 10.0, "doors", [
    ("id",          "INT PK",      True,  False),
    ("name",        "VARCHAR(120)",False, False),
    ("location",    "VARCHAR(200)",False, False),
    ("is_locked",   "BOOLEAN",     False, False),
    ("method_pin",  "BOOLEAN",     False, False),
    ("method_fp",   "BOOLEAN",     False, False),
    ("method_face", "BOOLEAN",     False, False),
    ("last_access", "DATETIME",    False, False),
], "main", w=W)

# pin_codes
pc = er_table(ax2, 0.5, 8.0, "pin_codes", [
    ("id",         "INT PK",  True,  False),
    ("user_id",    "INT FK",  False, True),
    ("pin_hash",   "VARCHAR(256)", False, False),
    ("is_active",  "BOOLEAN", False, False),
    ("expires_at", "DATETIME",False, False),
], "cred", w=W)

# fingerprints
fp = er_table(ax2, 0.5, 5.5, "fingerprints", [
    ("id",           "INT PK",      True,  False),
    ("user_id",      "INT FK",      False, True),
    ("template_ref", "VARCHAR(200)",False, False),
    ("is_active",    "BOOLEAN",     False, False),
    ("enrolled_at",  "DATETIME",    False, False),
], "cred", w=W)

# face_encodings
fe = er_table(ax2, 0.5, 3.1, "face_encodings", [
    ("id",          "INT PK",       True,  False),
    ("user_id",     "INT FK",       False, True),
    ("label",       "VARCHAR(120)", False, False),
    ("encoding",    "LONGBLOB",     False, False),
    ("is_active",   "BOOLEAN",      False, False),
    ("enrolled_at", "DATETIME",     False, False),
], "cred", w=W)

# access_logs
al = er_table(ax2, 6.2, 5.8, "access_logs", [
    ("id",        "INT PK",     True,  False),
    ("door_id",   "INT FK",     False, True),
    ("user_id",   "INT FK",     False, True),
    ("method",    "VARCHAR(20)",False, False),
    ("success",   "BOOLEAN",    False, False),
    ("notes",     "VARCHAR(300)",False,False),
    ("timestamp", "DATETIME",   False, False),
], "log", w=W)

# junction tables
pcd = er_table(ax2, 6.2, 8.2, "pin_code_doors", [
    ("pin_code_id","INT FK PK", True, True),
    ("door_id",    "INT FK PK", True, True),
], "junction", w=2.6)

fpd = er_table(ax2, 9.5, 6.0, "fingerprint_doors", [
    ("fingerprint_id","INT FK PK", True, True),
    ("door_id",       "INT FK PK", True, True),
], "junction", w=2.7)

fed = er_table(ax2, 9.5, 3.8, "face_encoding_doors", [
    ("face_encoding_id","INT FK PK", True, True),
    ("door_id",         "INT FK PK", True, True),
], "junction", w=2.7)

# ── Relationship arrows ───────────────────────────────────
# users → pin_codes (1:N)
ax2.annotate("", xy=(0.5 + W/2, 8.0), xytext=(6.2 + W/2 - 0.05, 10.0 - 2.5),
             arrowprops=dict(arrowstyle="->", color="#2471a3", lw=1.2,
                             connectionstyle="arc3,rad=0.1"), zorder=2)
ax2.text(4.5, 7.65, "1:N", fontsize=6.5, color="#2471a3")

# users → fingerprints (1:N)
ax2.annotate("", xy=(0.5 + W/2, 5.5), xytext=(6.2 + W/2 - 0.1, 10.0 - 2.8),
             arrowprops=dict(arrowstyle="->", color="#2471a3", lw=1.2,
                             connectionstyle="arc3,rad=0.15"), zorder=2)
ax2.text(3.3, 5.6, "1:N", fontsize=6.5, color="#2471a3")

# users → face_encodings (1:N)
ax2.annotate("", xy=(0.5 + W/2, 3.1), xytext=(6.2 + W/2 - 0.15, 10.0 - 3.0),
             arrowprops=dict(arrowstyle="->", color="#2471a3", lw=1.2,
                             connectionstyle="arc3,rad=0.2"), zorder=2)
ax2.text(2.8, 4.0, "1:N", fontsize=6.5, color="#2471a3")

# users → access_logs (1:N)
ax2.annotate("", xy=(6.2 + W/2 - 0.3, 5.8), xytext=(6.2 + W/2, 10.0 - 2.55),
             arrowprops=dict(arrowstyle="->", color="#7d3c98", lw=1.2,
                             connectionstyle="arc3,rad=0.0"), zorder=2)
ax2.text(7.7, 7.5, "1:N", fontsize=6.5, color="#7d3c98")

# doors → access_logs (1:N)
ax2.annotate("", xy=(6.2 + W, 5.8 - 1.2), xytext=(12.5 + W/2 - 0.2, 10.0 - 2.5),
             arrowprops=dict(arrowstyle="->", color="#7d3c98", lw=1.2,
                             connectionstyle="arc3,rad=-0.1"), zorder=2)
ax2.text(10.8, 6.5, "1:N", fontsize=6.5, color="#7d3c98")

# pin_codes ↔ doors via pin_code_doors
ax2.annotate("", xy=(6.2, 8.2 - 0.6), xytext=(0.5 + W, 8.0 - 1.1),
             arrowprops=dict(arrowstyle="->", color="#b7950b", lw=1.1,
                             connectionstyle="arc3,rad=0.0"), zorder=2)
ax2.annotate("", xy=(6.2 + 2.6, 8.2 - 0.6), xytext=(12.5, 10.0 - 2.0),
             arrowprops=dict(arrowstyle="->", color="#b7950b", lw=1.1,
                             connectionstyle="arc3,rad=0.1"), zorder=2)
ax2.text(6.9, 7.25, "N:M", fontsize=6.5, color="#b7950b")

# fingerprints ↔ doors via fingerprint_doors
ax2.annotate("", xy=(9.5, 6.0 - 0.6), xytext=(0.5 + W, 5.5 - 1.1),
             arrowprops=dict(arrowstyle="->", color="#b7950b", lw=1.1,
                             connectionstyle="arc3,rad=-0.05"), zorder=2)
ax2.annotate("", xy=(9.5 + 2.7, 6.0 - 0.6), xytext=(12.5, 10.0 - 3.0),
             arrowprops=dict(arrowstyle="->", color="#b7950b", lw=1.1,
                             connectionstyle="arc3,rad=0.05"), zorder=2)
ax2.text(7.2, 5.0, "N:M", fontsize=6.5, color="#b7950b")

# face_encodings ↔ doors via face_encoding_doors
ax2.annotate("", xy=(9.5, 3.8 - 0.65), xytext=(0.5 + W, 3.1 - 1.25),
             arrowprops=dict(arrowstyle="->", color="#b7950b", lw=1.1,
                             connectionstyle="arc3,rad=-0.08"), zorder=2)
ax2.annotate("", xy=(9.5 + 2.7, 3.8 - 0.65), xytext=(12.5, 10.0 - 4.5),
             arrowprops=dict(arrowstyle="->", color="#b7950b", lw=1.1,
                             connectionstyle="arc3,rad=0.1"), zorder=2)
ax2.text(7.5, 3.0, "N:M", fontsize=6.5, color="#b7950b")

# Legend
legend_items2 = [
    mpatches.Patch(fc=COLORS["main"][0],     ec=COLORS["main"][1],     label="Основни таблици"),
    mpatches.Patch(fc=COLORS["cred"][0],     ec=COLORS["cred"][1],     label="Идентификационни данни"),
    mpatches.Patch(fc=COLORS["junction"][0], ec=COLORS["junction"][1], label="Junction (N:M)"),
    mpatches.Patch(fc=COLORS["log"][0],      ec=COLORS["log"][1],      label="Одит лог"),
]
ax2.legend(handles=legend_items2, loc="lower right", fontsize=8,
           framealpha=0.95, edgecolor="#aaa", fancybox=True)

# Icon note
ax2.text(0.3, 0.25, "[PK] = Primary Key        [FK] = Foreign Key",
         fontsize=7.5, color="#555", va="center")

plt.tight_layout()
plt.savefig(f"{OUT}/er_diagram.png", dpi=180, bbox_inches="tight",
            facecolor=fig2.get_facecolor())
plt.close()
print("✓ er_diagram.png saved")
