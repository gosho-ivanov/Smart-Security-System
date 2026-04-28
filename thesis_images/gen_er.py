"""ER diagram — clean grid layout, orthogonal connectors."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np

OUT = "/Users/thanatos/Documents/school/Final project/thesis_images"

# ── Palette ────────────────────────────────────────────────
C = {
    "main_fc":  "#dce8f5", "main_ec":  "#1565c0",   # users / doors
    "cred_fc":  "#d5f5e3", "cred_ec":  "#1b5e20",   # credentials
    "junc_fc":  "#fff8e1", "junc_ec":  "#e65100",   # junction
    "log_fc":   "#f3e5f5", "log_ec":   "#6a1b9a",   # access_logs
    "arr_uc":   "#1565c0",   # user→cred arrow
    "arr_cj":   "#1b5e20",   # cred→junction arrow
    "arr_jd":   "#e65100",   # junction→doors arrow
    "arr_al":   "#6a1b9a",   # →access_logs arrow
}

ROW_H    = 0.315
HDR_H    = 0.43
BODY_PAD = 0.05

def tbl_h(n): return n * ROW_H + BODY_PAD + HDR_H

# ── Table renderer ─────────────────────────────────────────
def table(ax, left, top, w, title, fields, fc, ec):
    n   = len(fields)
    th  = tbl_h(n)
    bot = top - th
    cx  = left + w / 2

    # header
    ax.add_patch(FancyBboxPatch(
        (left, top - HDR_H), w, HDR_H,
        boxstyle="round,pad=0", fc=ec, ec=ec, lw=0, zorder=3))
    ax.text(cx, top - HDR_H / 2, title,
            ha="center", va="center", fontsize=8.5,
            fontweight="bold", color="white", zorder=4)

    # body
    ax.add_patch(FancyBboxPatch(
        (left, bot), w, th - HDR_H,
        boxstyle="round,pad=0", fc=fc, ec=ec, lw=1.4, zorder=3))

    for i, (name, typ, is_pk, is_fk) in enumerate(fields):
        fy = top - HDR_H - (i + 0.5) * ROW_H
        tag   = "PK" if is_pk else ("FK" if is_fk else "  ")
        tcol  = "#c62828" if is_pk else ("#1565c0" if is_fk else "#aaa")
        ax.text(left + 0.13, fy, f"[{tag}]",
                ha="left", va="center", fontsize=6.2,
                color=tcol, fontweight="bold", zorder=4)
        ax.text(left + 0.72, fy, name,
                ha="left", va="center", fontsize=7.0, color="#1a1a1a", zorder=4)
        ax.text(left + w - 0.10, fy, typ,
                ha="right", va="center", fontsize=5.8, color="#777", zorder=4)
        if i < n - 1:
            ay = fy - ROW_H / 2
            ax.plot([left + 0.06, left + w - 0.06], [ay, ay],
                    color="#ddd", lw=0.5, zorder=4)

    right    = left + w
    mid_y    = top - th / 2
    return dict(l=(left, mid_y), r=(right, mid_y),
                t=(cx, top),    b=(cx, bot),
                left=left, right=right, top=top, bot=bot,
                cx=cx, mid_y=mid_y, w=w, h=th)


# ── Orthogonal arrow ───────────────────────────────────────
def ortho(ax, pts, color, lw=1.25):
    """Draw path through pts, arrowhead at last point."""
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    ax.plot(xs, ys, color=color, lw=lw, zorder=2,
            solid_capstyle="round", solid_joinstyle="round")
    # arrowhead
    px, py = pts[-2]
    ex, ey = pts[-1]
    d = ((ex-px)**2 + (ey-py)**2) ** 0.5
    eps = 0.05
    ax.annotate("",
                xy=(ex, ey),
                xytext=(ex - (ex-px)/d*eps, ey - (ey-py)/d*eps),
                arrowprops=dict(arrowstyle="-|>", color=color,
                                lw=lw, mutation_scale=11),
                zorder=3)


def card(ax, x, y, text, color):
    ax.text(x, y, text, ha="center", va="center", fontsize=7.5,
            fontweight="bold", color=color, zorder=5,
            bbox=dict(fc="white", ec="none", pad=1.5))


# ─────────────────────────────────────────────────────────
# LAYOUT  (18 × 12.5 canvas)
# columns: users | cred-tables | junction-tables | doors
# rows (top y): 11.5 / 8.7 / 5.9     + access_logs at 3.0
# ─────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(18, 12.5))
ax.set_xlim(0, 18)
ax.set_ylim(0, 12.5)
ax.axis("off")
fig.patch.set_facecolor("#f7f9fc")
ax.set_facecolor("#f7f9fc")

ax.text(9, 12.15,
        "ER диаграма — База данни: security_system",
        ha="center", va="center", fontsize=14,
        fontweight="bold", color="#1a1a2e")

# ── Column / row anchors ───────────────────────────────────
C1L = 0.25   # users left
C2L = 4.65   # credential tables left
C3L = 9.35   # junction tables left
C4L = 13.55  # doors left

WU = 3.75    # users / doors width
WC = 4.20    # credential width
WJ = 3.70    # junction width

R1 = 11.5    # top y for row 1
R2 =  8.7    # top y for row 2
R3 =  5.9    # top y for row 3
AL_TOP = 3.0 # access_logs top

# ── Draw tables ────────────────────────────────────────────
U = table(ax, C1L, R1, WU, "users", [
    ("id",            "INT",         True,  False),
    ("name",          "VARCHAR(120)",False, False),
    ("username",      "VARCHAR(80)", False, False),
    ("email",         "VARCHAR(200)",False, False),
    ("password_hash", "VARCHAR(256)",False, False),
    ("role",          "VARCHAR(40)", False, False),
    ("is_active",     "BOOLEAN",     False, False),
    ("last_login",    "DATETIME",    False, False),
], C["main_fc"], C["main_ec"])

D = table(ax, C4L, R1, WU, "doors", [
    ("id",          "INT",         True,  False),
    ("name",        "VARCHAR(120)",False, False),
    ("location",    "VARCHAR(200)",False, False),
    ("is_locked",   "BOOLEAN",     False, False),
    ("method_pin",  "BOOLEAN",     False, False),
    ("method_fp",   "BOOLEAN",     False, False),
    ("method_face", "BOOLEAN",     False, False),
    ("last_access", "DATETIME",    False, False),
], C["main_fc"], C["main_ec"])

PC = table(ax, C2L, R1, WC, "pin_codes", [
    ("id",         "INT",         True,  False),
    ("user_id",    "INT",         False, True),
    ("pin_hash",   "VARCHAR(256)",False, False),
    ("is_active",  "BOOLEAN",     False, False),
    ("expires_at", "DATETIME",    False, False),
], C["cred_fc"], C["cred_ec"])

FP = table(ax, C2L, R2, WC, "fingerprints", [
    ("id",           "INT",         True,  False),
    ("user_id",      "INT",         False, True),
    ("template_ref", "VARCHAR(200)",False, False),
    ("is_active",    "BOOLEAN",     False, False),
    ("enrolled_at",  "DATETIME",    False, False),
], C["cred_fc"], C["cred_ec"])

FE = table(ax, C2L, R3, WC, "face_encodings", [
    ("id",          "INT",         True,  False),
    ("user_id",     "INT",         False, True),
    ("label",       "VARCHAR(120)",False, False),
    ("encoding",    "LONGBLOB",    False, False),
    ("is_active",   "BOOLEAN",     False, False),
    ("enrolled_at", "DATETIME",    False, False),
], C["cred_fc"], C["cred_ec"])

PCD = table(ax, C3L, R1, WJ, "pin_code_doors", [
    ("pin_code_id", "INT FK+PK", True, True),
    ("door_id",     "INT FK+PK", True, True),
], C["junc_fc"], C["junc_ec"])

FPD = table(ax, C3L, R2, WJ, "fingerprint_doors", [
    ("fingerprint_id", "INT FK+PK", True, True),
    ("door_id",        "INT FK+PK", True, True),
], C["junc_fc"], C["junc_ec"])

FED = table(ax, C3L, R3, WJ, "face_encoding_doors", [
    ("face_encoding_id", "INT FK+PK", True, True),
    ("door_id",          "INT FK+PK", True, True),
], C["junc_fc"], C["junc_ec"])

AL = table(ax, 6.4, AL_TOP, 5.2, "access_logs", [
    ("id",        "INT",         True,  False),
    ("door_id",   "INT",         False, True),
    ("user_id",   "INT",         False, True),
    ("method",    "VARCHAR(20)", False, False),
    ("success",   "BOOLEAN",     False, False),
    ("notes",     "VARCHAR(300)",False, False),
    ("timestamp", "DATETIME",    False, False),
], C["log_fc"], C["log_ec"])

# ─────────────────────────────────────────────────────────
# ARROWS
# ─────────────────────────────────────────────────────────

# ── users → pin_codes  (1:N, straight right from upper zone of users) ─────
# Connect from users right edge at pin_codes mid_y level
pc_y = PC["mid_y"]
ortho(ax, [(U["right"], pc_y), (PC["left"], pc_y)], C["arr_uc"])
card(ax, U["right"] + 0.18, pc_y + 0.20, "1", C["arr_uc"])
card(ax, PC["left"] - 0.18, pc_y + 0.20, "N", C["arr_uc"])

# ── users → fingerprints  (1:N, elbow down then right) ────────────────────
via_x_fp = C2L - 0.55
ortho(ax, [(U["right"], U["mid_y"]),
           (via_x_fp,   U["mid_y"]),
           (via_x_fp,   FP["mid_y"]),
           (FP["left"], FP["mid_y"])], C["arr_uc"])
card(ax, via_x_fp + 0.15, (U["mid_y"] + FP["mid_y"]) / 2, "1:N", C["arr_uc"])

# ── users → face_encodings  (1:N, elbow further down) ─────────────────────
via_x_fe = C2L - 0.90
ortho(ax, [(U["right"], U["bot"]),
           (via_x_fe,   U["bot"]),
           (via_x_fe,   FE["mid_y"]),
           (FE["left"], FE["mid_y"])], C["arr_uc"])
card(ax, via_x_fe + 0.15, (U["bot"] + FE["mid_y"]) / 2, "1:N", C["arr_uc"])

# ── users → access_logs  (1:N, down from users bottom-center) ─────────────
# Drop a vertical down from users bottom, then horizontal to AL left
al_mid = AL["mid_y"]
u_drop_x = U["cx"]
ortho(ax, [(u_drop_x,  U["bot"]),
           (u_drop_x,  al_mid),
           (AL["left"], al_mid)], C["arr_al"])
card(ax, (u_drop_x + AL["left"]) / 2, al_mid + 0.20, "1:N", C["arr_al"])

# ── doors → access_logs  (1:N, down from doors bottom, right to AL right) ─
d_drop_x = D["cx"]
ortho(ax, [(d_drop_x,   D["bot"]),
           (d_drop_x,   al_mid),
           (AL["right"], al_mid)], C["arr_al"])
card(ax, (d_drop_x + AL["right"]) / 2, al_mid + 0.20, "1:N", C["arr_al"])

# ── pin_codes → pin_code_doors  (N, right then elbow if needed) ───────────
ortho(ax, [(PC["right"], PC["mid_y"]), (PCD["left"], PCD["mid_y"])], C["arr_cj"])
card(ax, (PC["right"] + PCD["left"]) / 2, PC["mid_y"] + 0.18, "N", C["arr_cj"])

# ── fingerprints → fingerprint_doors ──────────────────────────────────────
ortho(ax, [(FP["right"], FP["mid_y"]), (FPD["left"], FPD["mid_y"])], C["arr_cj"])
card(ax, (FP["right"] + FPD["left"]) / 2, FP["mid_y"] + 0.18, "N", C["arr_cj"])

# ── face_encodings → face_encoding_doors ──────────────────────────────────
ortho(ax, [(FE["right"], FE["mid_y"]), (FED["left"], FED["mid_y"])], C["arr_cj"])
card(ax, (FE["right"] + FED["left"]) / 2, FE["mid_y"] + 0.18, "N", C["arr_cj"])

# ── pin_code_doors → doors  (N, elbow right then down/up to doors left) ───
# connect to doors left at a y inside doors' body (upper third)
d_attach_pc  = D["top"]  - D["h"] * 0.25
d_attach_fp  = D["mid_y"]
d_attach_fe  = D["top"]  - D["h"] * 0.75
via_x_jd     = D["left"] - 0.50

ortho(ax, [(PCD["right"], PCD["mid_y"]),
           (via_x_jd,     PCD["mid_y"]),
           (via_x_jd,     d_attach_pc),
           (D["left"],    d_attach_pc)], C["arr_jd"])
card(ax, via_x_jd - 0.22, (PCD["mid_y"] + d_attach_pc) / 2, "N", C["arr_jd"])

ortho(ax, [(FPD["right"], FPD["mid_y"]),
           (via_x_jd,     FPD["mid_y"]),
           (via_x_jd,     d_attach_fp),
           (D["left"],    d_attach_fp)], C["arr_jd"])

ortho(ax, [(FED["right"], FED["mid_y"]),
           (via_x_jd,     FED["mid_y"]),
           (via_x_jd,     d_attach_fe),
           (D["left"],    d_attach_fe)], C["arr_jd"])
card(ax, via_x_jd - 0.22, (FED["mid_y"] + d_attach_fe) / 2, "N", C["arr_jd"])

# ── Legend ─────────────────────────────────────────────────
legend_items = [
    mpatches.Patch(fc=C["main_fc"], ec=C["main_ec"], lw=1.5, label="Основни таблици (users, doors)"),
    mpatches.Patch(fc=C["cred_fc"], ec=C["cred_ec"], lw=1.5, label="Идентификационни данни"),
    mpatches.Patch(fc=C["junc_fc"], ec=C["junc_ec"], lw=1.5, label="Junction таблици (N:M)"),
    mpatches.Patch(fc=C["log_fc"],  ec=C["log_ec"],  lw=1.5, label="Одит лог"),
]
ax.legend(handles=legend_items, loc="lower left", fontsize=8.5,
          framealpha=0.95, edgecolor="#bbb", fancybox=True, ncol=2)

ax.text(9, 0.15, "[PK] = Primary Key     [FK] = Foreign Key",
        ha="center", va="center", fontsize=8, color="#555")

plt.tight_layout(pad=0.3)
plt.savefig(f"{OUT}/er_diagram.png", dpi=160, bbox_inches="tight",
            facecolor=fig.get_facecolor())
plt.close()
print("✓ er_diagram.png saved")
