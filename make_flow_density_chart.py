import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np

# ===== シミュレーション（index.html）と同じパラメータ・モデル =====
VFREE = 2000 / 3      # 自由走行速度 40km/h (m/min)
CARLEN = 3             # 車長 (m)
JAMGAP = 3             # 最低車間 (m)
K_JAM = 1000 / (CARLEN + JAMGAP)  # ジャム密度 (台/km)


def v_eq(r):
    """車間距離 r(m) に対する平衡速度 (m/min)"""
    r = np.asarray(r, dtype=float)
    v = VFREE * (1 - JAMGAP / np.where(r > 0, r, np.nan))
    v = np.where(r <= JAMGAP, 0, v)
    return np.clip(v, 0, VFREE)


def q_of_k(k):
    """密度 k(台/km) に対する流量 q(台/min)"""
    k = np.asarray(k, dtype=float)
    h = np.where(k > 0, 1000 / k, np.inf)   # 車頭間隔 (m/台)
    r = h - CARLEN                          # 車間距離 (m)
    return v_eq(r) * k / 1000


# 臨界密度の解析解: r* = JAMGAP + sqrt(JAMGAP*(JAMGAP+CARLEN))
R_CRIT = JAMGAP + np.sqrt(JAMGAP * (JAMGAP + CARLEN))
K_CRIT = 1000 / (R_CRIT + CARLEN)
Q_CRIT = q_of_k(K_CRIT)

# ===== 日本語フォント設定 =====
for name in ["Yu Gothic", "Meiryo", "MS Gothic", "Noto Sans CJK JP", "IPAexGothic"]:
    if any(name.lower() in f.name.lower() for f in fm.fontManager.ttflist):
        plt.rcParams["font.family"] = name
        break
plt.rcParams["axes.unicode_minus"] = False

# ===== 描画 =====
k = np.linspace(0.01, K_JAM, 600)
q = q_of_k(k)

fig, ax = plt.subplots(figsize=(8, 5), dpi=160)
ax.plot(k, q, color="#1f9e9e", linewidth=2.5, label="流量-密度カーブ q(k)")
ax.axvline(K_CRIT, color="#e08a1e", linestyle="--", linewidth=1.6,
           label=f"臨界密度 k_c ≒ {K_CRIT:.1f} 台/km")
ax.plot([K_CRIT], [Q_CRIT], "o", color="#e08a1e", markersize=7, zorder=5)
ax.annotate(f"最大流量\nq_max ≒ {Q_CRIT:.2f} 台/min",
            xy=(K_CRIT, Q_CRIT), xytext=(K_CRIT + K_JAM * 0.08, Q_CRIT * 0.75),
            arrowprops=dict(arrowstyle="->", color="#555"), fontsize=10, color="#333")

ax.axvline(K_JAM, color="#c0392b", linestyle=":", linewidth=1.4, alpha=0.8)
ax.text(K_JAM, ax.get_ylim()[1] * 0.02, f" ジャム密度 ≒ {K_JAM:.0f} 台/km",
        rotation=90, va="bottom", ha="right", fontsize=9, color="#c0392b")

# 順調／渋滞の領域を色分け
ax.axvspan(0, K_CRIT, color="#3ad07a", alpha=0.08)
ax.axvspan(K_CRIT, K_JAM, color="#ff5a52", alpha=0.08)
ax.text(K_CRIT * 0.45, Q_CRIT * 1.06, "順調", fontsize=11, color="#1a7a4a", ha="center")
ax.text((K_CRIT + K_JAM) / 2, Q_CRIT * 1.06, "渋滞", fontsize=11, color="#a5332c", ha="center")

ax.set_xlim(0, K_JAM * 1.02)
ax.set_ylim(0, Q_CRIT * 1.2)
ax.set_xlabel("密度 k（台/km）")
ax.set_ylabel("流量 q（台/min）")
ax.set_title("交差点進入路の基本図（流量-密度関係）と臨界密度")
ax.grid(alpha=0.25)
ax.legend(loc="upper right", fontsize=9, framealpha=0.9)

fig.tight_layout()
out_path = "臨界密度_基本図.png"
fig.savefig(out_path, facecolor="white")
print("saved:", out_path, " K_CRIT=", K_CRIT, " Q_CRIT=", Q_CRIT)
