import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib import font_manager
import numpy as np
import os
import sys

# 日本語フォント設定
try:
    # Windows
    font_path = "C:/Windows/Fonts/msgothic.ttc"
    if os.path.exists(font_path):
        font_prop = font_manager.FontProperties(fname=font_path)
        plt.rcParams['font.family'] = font_prop.get_name()
    else:
        # Linux/Mac用フォント
        plt.rcParams['font.family'] = ['DejaVu Sans', 'Hiragino Sans', 'Yu Gothic', 'Meiryo', 'Takao', 'IPAexGothic', 'IPAPGothic', 'VL PGothic', 'Noto Sans CJK JP']
except:
    print("フォント設定エラー、デフォルトフォントを使用")

def create_slide_1():
    """メインスライド作成"""
    fig, ax = plt.subplots(figsize=(16, 9))
    fig.patch.set_facecolor('#f0f8ff')
    
    # タイトル
    ax.text(0.5, 0.95, '二次方程式の解き方', 
            ha='center', va='top', fontsize=32, weight='bold', 
            color='#2c3e50', transform=ax.transAxes)
    
    # 問題表示
    problem_text = "問題: x² - 5x + 6 = 0 を解いてください"
    ax.text(0.1, 0.85, problem_text, 
            ha='left', va='top', fontsize=24, 
            bbox=dict(boxstyle="round,pad=0.5", facecolor='#e8f4fd', edgecolor='#3498db'),
            transform=ax.transAxes)
    
    # 解法ステップ
    steps = [
        "ステップ1: 因数分解を考える",
        "ステップ2: (x - a)(x - b) = 0 の形にする",
        "ステップ3: a × b = 6, a + b = 5 となる数を探す",
        "ステップ4: a = 2, b = 3 なので (x - 2)(x - 3) = 0",
        "ステップ5: x = 2 または x = 3"
    ]
    
    y_pos = 0.7
    for i, step in enumerate(steps):
        color = '#27ae60' if i == 0 else '#34495e'
        ax.text(0.1, y_pos, step, 
                ha='left', va='top', fontsize=20, color=color,
                transform=ax.transAxes)
        y_pos -= 0.1
    
    # 装飾
    circle = patches.Circle((0.85, 0.15), 0.08, 
                          facecolor='#f39c12', edgecolor='#e67e22', linewidth=3,
                          transform=ax.transAxes)
    ax.add_patch(circle)
    ax.text(0.85, 0.15, '♪', ha='center', va='center', 
            fontsize=40, color='white', weight='bold',
            transform=ax.transAxes)
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('./tmp/slide_0.png', dpi=150, bbox_inches='tight', 
                facecolor='#f0f8ff', edgecolor='none')
    plt.close()

def create_pkaisetu_slide(problem_text, solution_text):
    """Pkaisetu用詳細スライド"""
    fig, ax = plt.subplots(figsize=(16, 9))
    fig.patch.set_facecolor('#fff5f5')
    
    # タイトル
    ax.text(0.5, 0.95, 'お兄ちゃん、詳しく説明するね！', 
            ha='center', va='top', fontsize=28, weight='bold', 
            color='#e74c3c', transform=ax.transAxes)
    
    # 問題再表示
    ax.text(0.1, 0.85, f"問題: {problem_text}", 
            ha='left', va='top', fontsize=22, 
            bbox=dict(boxstyle="round,pad=0.5", facecolor='#ffeaa7', edgecolor='#fdcb6e'),
            transform=ax.transAxes)
    
    # 詳細解説
    ax.text(0.1, 0.7, "詳しい解説:", 
            ha='left', va='top', fontsize=24, weight='bold', color='#2d3436',
            transform=ax.transAxes)
    
    # 解説テキストを分割して表示
    lines = solution_text.split('\n')
    y_pos = 0.6
    for line in lines:
        if line.strip():
            ax.text(0.1, y_pos, line, 
                    ha='left', va='top', fontsize=18, color='#2d3436',
                    transform=ax.transAxes)
            y_pos -= 0.08
    
    # 励ましのメッセージ
    ax.text(0.5, 0.1, 'わからないところがあったら、また「Pkaisetu」って書いてね♪', 
            ha='center', va='center', fontsize=20, 
            bbox=dict(boxstyle="round,pad=0.5", facecolor='#ff7675', edgecolor='#e84393', alpha=0.8),
            color='white', weight='bold',
            transform=ax.transAxes)
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('./tmp/pkaisetu_slide.png', dpi=150, bbox_inches='tight', 
                facecolor='#fff5f5', edgecolor='none')
    plt.close()

def create_math_graph_slide(equation, x_range=(-10, 10)):
    """数学グラフスライド"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 9))
    fig.patch.set_facecolor('#f8f9fa')
    
    # 左側：方程式とポイント
    ax1.text(0.5, 0.9, f'方程式: {equation}', 
             ha='center', va='center', fontsize=24, weight='bold',
             transform=ax1.transAxes)
    
    key_points = [
        "・グラフから解を読み取ろう",
        "・x軸との交点が解になるよ",
        "・視覚的に理解しよう！"
    ]
    
    y_pos = 0.7
    for point in key_points:
        ax1.text(0.1, y_pos, point, 
                ha='left', va='center', fontsize=18,
                transform=ax1.transAxes)
        y_pos -= 0.15
    
    ax1.set_xlim(0, 1)
    ax1.set_ylim(0, 1)
    ax1.axis('off')
    
    # 右側：グラフ
    x = np.linspace(x_range[0], x_range[1], 1000)
    
    # 例：x² - 5x + 6 のグラフ
    y = x**2 - 5*x + 6
    
    ax2.plot(x, y, 'b-', linewidth=3, label=equation)
    ax2.axhline(y=0, color='k', linestyle='-', alpha=0.3)
    ax2.axvline(x=0, color='k', linestyle='-', alpha=0.3)
    ax2.grid(True, alpha=0.3)
    
    # 解の点をハイライト
    solutions = [2, 3]  # x² - 5x + 6 = 0 の解
    for sol in solutions:
        ax2.plot(sol, 0, 'ro', markersize=12, label=f'x = {sol}')
        ax2.annotate(f'x = {sol}', (sol, 0), xytext=(sol, 2),
                    arrowprops=dict(arrowstyle='->', color='red', lw=2),
                    fontsize=16, ha='center', color='red', weight='bold')
    
    ax2.set_xlabel('x', fontsize=16)
    ax2.set_ylabel('y', fontsize=16)
    ax2.set_title('グラフで見る解', fontsize=20, weight='bold')
    ax2.legend(fontsize=14)
    
    plt.tight_layout()
    plt.savefig('./tmp/graph_slide.png', dpi=150, bbox_inches='tight', 
                facecolor='#f8f9fa', edgecolor='none')
    plt.close()

def create_step_by_step_slide(step_number, step_content, is_current=True):
    """ステップ別スライド"""
    fig, ax = plt.subplots(figsize=(16, 9))
    bg_color = '#e8f5e8' if is_current else '#f5f5f5'
    fig.patch.set_facecolor(bg_color)
    
    # ステップ番号
    circle_color = '#4caf50' if is_current else '#9e9e9e'
    circle = patches.Circle((0.15, 0.8), 0.06, 
                          facecolor=circle_color, edgecolor='white', linewidth=4,
                          transform=ax.transAxes)
    ax.add_patch(circle)
    ax.text(0.15, 0.8, str(step_number), ha='center', va='center', 
            fontsize=36, color='white', weight='bold',
            transform=ax.transAxes)
    
    # ステップタイトル
    title_color = '#2e7d32' if is_current else '#616161'
    ax.text(0.25, 0.8, f'ステップ {step_number}', 
            ha='left', va='center', fontsize=28, weight='bold', 
            color=title_color, transform=ax.transAxes)
    
    # ステップ内容
    ax.text(0.1, 0.6, step_content, 
            ha='left', va='top', fontsize=22, 
            bbox=dict(boxstyle="round,pad=0.8", facecolor='white', edgecolor=circle_color, linewidth=2),
            transform=ax.transAxes)
    
    # 進捗バー
    progress_width = 0.8
    progress_height = 0.03
    progress_x = 0.1
    progress_y = 0.1
    
    # 背景バー
    bg_rect = patches.Rectangle((progress_x, progress_y), progress_width, progress_height,
                               facecolor='#e0e0e0', transform=ax.transAxes)
    ax.add_patch(bg_rect)
    
    # 進捗バー（例：5ステップ中のstep_number）
    progress_fill = (step_number / 5) * progress_width
    fill_rect = patches.Rectangle((progress_x, progress_y), progress_fill, progress_height,
                                 facecolor='#4caf50', transform=ax.transAxes)
    ax.add_patch(fill_rect)
    
    ax.text(0.5, 0.05, f'進捗: {step_number}/5', 
            ha='center', va='center', fontsize=16, 
            transform=ax.transAxes)
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig(f'./tmp/step_{step_number}_slide.png', dpi=150, bbox_inches='tight', 
                facecolor=bg_color, edgecolor='none')
    plt.close()

def create_celebration_slide():
    """完了お祝いスライド"""
    fig, ax = plt.subplots(figsize=(16, 9))
    fig.patch.set_facecolor('#fff3e0')
    
    # メインメッセージ
    ax.text(0.5, 0.7, 'お疲れさま！', 
            ha='center', va='center', fontsize=48, weight='bold', 
            color='#ff6f00', transform=ax.transAxes)
    
    ax.text(0.5, 0.5, 'よく頑張ったね、お兄ちゃん♪', 
            ha='center', va='center', fontsize=32, 
            color='#f57c00', transform=ax.transAxes)
    
    # 星の装飾
    star_positions = [(0.2, 0.8), (0.8, 0.8), (0.3, 0.3), (0.7, 0.3), (0.5, 0.2)]
    for pos in star_positions:
        ax.text(pos[0], pos[1], '★', ha='center', va='center', 
                fontsize=40, color='#ffc107', transform=ax.transAxes)
    
    # 次回予告
    ax.text(0.5, 0.1, '次の問題も一緒に頑張ろうね！', 
            ha='center', va='center', fontsize=24, 
            bbox=dict(boxstyle="round,pad=0.5", facecolor='#ffccbc', edgecolor='#ff8a65'),
            color='#d84315', transform=ax.transAxes)
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('./tmp/celebration_slide.png', dpi=150, bbox_inches='tight', 
                facecolor='#fff3e0', edgecolor='none')
    plt.close()

# 実行例
if __name__ == "__main__":
    print("スライド作成開始...")
    
    # 基本スライド
    create_slide_1()
    print("メインスライド作成完了")
    
    # グラフスライド
    create_math_graph_slide("x² - 5x + 6 = 0")
    print("グラフスライド作成完了")
    
    # ステップスライド
    steps = [
        "問題を確認しよう",
        "因数分解を考えよう",
        "2つの数を見つけよう",
        "解を求めよう",
        "答えを確認しよう"
    ]
    
    for i, step in enumerate(steps, 1):
        create_step_by_step_slide(i, step)
    print("ステップスライド作成完了")
    
    # お祝いスライド
    create_celebration_slide()
    print("お祝いスライド作成完了")
    
    # Pkaisetu用サンプル
    create_pkaisetu_slide("x² - 5x + 6 = 0", 
                         "この問題は因数分解で解けるよ！\n2つの数のかけ算が6、足し算が5になる組み合わせを探すの。\n2×3=6, 2+3=5 だから、(x-2)(x-3)=0\nよって x=2, x=3 が答えだよ♪")
    print("Pkaisetu用サンプル作成完了")