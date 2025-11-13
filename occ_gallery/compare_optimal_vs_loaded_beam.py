#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
曲率変化最適化はり vs 静荷重実際はりの比較デモンストレーション
最適な応力分散がされているはりと実際の荷重下はりの違いを可視化

Created on: 2025-11-13
Author: GitHub Copilot & User
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import font_manager
import sys
import os

# 日本語フォント設定（Windows環境対応）
plt.rcParams['font.family'] = ['DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# Windowsで利用可能な日本語フォントを自動検出
import platform
if platform.system() == 'Windows':
    try:
        # Windows標準の日本語フォントを試行
        available_fonts = [f.name for f in font_manager.fontManager.ttflist]
        japanese_fonts = ['Yu Gothic', 'Meiryo', 'MS Gothic', 'MS Mincho']
        for font in japanese_fonts:
            if font in available_fonts:
                plt.rcParams['font.family'] = [font, 'DejaVu Sans']
                break
    except:
        pass  # デフォルトフォントを使用

try:
    from OCC.Core import gp_Pnt, TColgp_HArray1OfPnt
    from OCC.Core import FairCurve_MinimalVariation
    from OCC.Display.SimpleGui import init_display
    HAS_OCC = True
except ImportError:
    print("Warning: OpenCASCADE not available. Using mathematical simulation only.")
    HAS_OCC = False

class BeamComparison:
    """同一荷重条件下での異なる形状はりの性能比較クラス"""
    
    def __init__(self, length=1000.0, E=210e9, I=8.33e-6, load_case='uniform'):
        """
        Parameters:
        -----------
        length : float
            はりの長さ (mm)
        E : float  
            ヤング率 (Pa)
        I : float
            断面二次モーメント (m^4)
        load_case : str
            荷重ケース ('uniform', 'point', 'distributed')
        """
        self.L = length
        self.E = E 
        self.I = I
        self.load_case = load_case
        
        # 解析用パラメータ
        self.n_points = 101
        self.x = np.linspace(0, self.L, self.n_points)
        
        print(f"Analysis - {load_case} loading")
        print(f"   Length: {self.L:.0f} mm")
        print(f"   Young's Modulus: {self.E/1e9:.0f} GPa") 
        print(f"   Moment of Inertia: {self.I*1e6:.2f} cm^4")
    
    def optimized_shape_under_load(self, load_intensity=1000.0):
        """曲率最適化形状に実荷重を適用した応答計算"""
        # Step 1: 最適化形状の定義（変断面想定）
        xi = self.x / self.L
        
        # 曲率最適化に基づく断面二次モーメント分布
        # 最適化理論: 等応力設計 → I(x) ∝ M(x)
        base_shape = xi**3 * (1-xi)**3  # 基本形状関数
        
        # Step 2: 実荷重による応答計算
        if self.load_case == 'uniform':
            w_response, w_xx_response, stress_response = self._optimized_uniform_load(load_intensity, base_shape)
        elif self.load_case == 'point':
            w_response, w_xx_response, stress_response = self._optimized_point_load(load_intensity, base_shape)
        else:
            w_response, w_xx_response, stress_response = self._optimized_distributed_load(load_intensity, base_shape)
            
        return w_response, w_xx_response, stress_response
    
    def loaded_beam_response(self, load_intensity=1000.0):
        """静荷重を受ける実際のはり応答"""
        
        if self.load_case == 'uniform':
            return self._uniform_load_beam(load_intensity)
        elif self.load_case == 'point':
            return self._point_load_beam(load_intensity)
        else:
            return self._distributed_load_beam(load_intensity)
    
    def _uniform_load_beam(self, q):
        """等分布荷重を受けるはり（両端単純支持）"""
        xi = self.x / self.L
        
        # たわみ式: w = (qL⁴/24EI) × xi(1-xi)(1-xi²)  
        # より正確には: w = (q/(24EI)) × x(L³ - 2Lx² + x³)
        w_loaded = (q / (24 * self.E * self.I)) * \
                   self.x * (self.L**3 - 2*self.L*self.x**2 + self.x**3)
        
        # 曲率（解析解）: w'' = -(q/2EI)(L² - 6Lx + 6x²)
        w_xx = -(q / (2 * self.E * self.I)) * \
               (self.L**2 - 6*self.L*self.x + 6*self.x**2)
        
        # 応力（符号付き）
        stress_loaded = w_xx * self.E * 0.05 / self.I
        
        return w_loaded, w_xx, stress_loaded
    
    def _point_load_beam(self, P):
        """中央集中荷重を受けるはり（両端単純支持）"""
        xi = self.x / self.L
        
        # たわみ式（中央荷重、連続関数として実装）
        w_loaded = np.zeros_like(xi)
        
        for i, x_val in enumerate(xi):
            if x_val <= 0.5:
                # 左半分: w = (Px/48EI)(3L² - 4x²)
                w_loaded[i] = (P * self.L**3) / (48 * self.E * self.I) * \
                             x_val * (3 - 4*x_val**2)
            else:
                # 右半分: w = (P/48EI)[3Lx² - 4x³ - (3L³/4 - L³)] (対称性利用)
                x_from_left = x_val
                w_loaded[i] = (P * self.L**3) / (48 * self.E * self.I) * \
                             (1-x_from_left) * (3 - 4*(1-x_from_left)**2)
        
        # 曲率（解析解）
        w_xx = np.zeros_like(xi)
        for i, x_val in enumerate(xi):
            if x_val <= 0.5:
                # 左半分: w'' = -(P/4EI)(L - 2x)
                w_xx[i] = -(P) / (4 * self.E * self.I) * (self.L - 2*x_val*self.L) / self.L**2
            else:
                # 右半分: w'' = -(P/4EI)(L - 2(L-x)) = -(P/4EI)(2x - L)
                w_xx[i] = -(P) / (4 * self.E * self.I) * (2*x_val*self.L - self.L) / self.L**2
        
        # 応力（符号付き）
        stress_loaded = w_xx * self.E * 0.05 / self.I
        
        return w_loaded, w_xx, stress_loaded
    
    def _distributed_load_beam(self, q):
        """部分分布荷重"""
        return self._uniform_load_beam(q * 0.6)  # 簡略化
    
    def _optimized_uniform_load(self, q, shape_func):
        """最適化形状に等分布荷重を適用"""
        # 変断面を考慮した解析的近似解
        xi = self.x / self.L
        
        # 形状関数に基づく断面二次モーメント変化
        I_ratio = 0.5 + 1.5 * shape_func  # I(x)/I_base
        
        # 近似変位（変断面効果を考慮）
        # 基本解に形状補正係数を適用
        w_base = (q / (24 * self.E * self.I)) * \
                 self.x * (self.L**3 - 2*self.L*self.x**2 + self.x**3)
        
        # 変断面による剛性増加効果
        stiffness_ratio = I_ratio
        w_optimized = w_base / stiffness_ratio
        
        # 曲率計算（数値微分）
        dx = self.x[1] - self.x[0]
        w_xx_optimized = np.gradient(np.gradient(w_optimized, dx), dx)
        
        # 応力計算（変断面考慮）
        stress_optimized = w_xx_optimized * self.E * 0.05 / (self.I * I_ratio)
        
        return w_optimized, w_xx_optimized, stress_optimized
        
    def _optimized_point_load(self, P, shape_func):
        """最適化形状に点荷重を適用"""
        xi = self.x / self.L
        
        # 形状関数に基づく断面変化
        I_ratio = 0.5 + 1.5 * shape_func
        
        # 基本点荷重解
        w_base = np.zeros_like(xi)
        for i, x_val in enumerate(xi):
            if x_val <= 0.5:
                w_base[i] = (P * self.L**3) / (48 * self.E * self.I) * \
                           x_val * (3 - 4*x_val**2)
            else:
                w_base[i] = (P * self.L**3) / (48 * self.E * self.I) * \
                           (1-x_val) * (3 - 4*(1-x_val)**2)
        
        # 変断面効果
        w_optimized = w_base / I_ratio
        
        # 曲率と応力
        dx = self.x[1] - self.x[0]
        w_xx_optimized = np.gradient(np.gradient(w_optimized, dx), dx)
        stress_optimized = w_xx_optimized * self.E * 0.05 / (self.I * I_ratio)
        
        return w_optimized, w_xx_optimized, stress_optimized
        
    def _optimized_distributed_load(self, q, shape_func):
        """最適化形状に分布荷重を適用"""
        return self._optimized_uniform_load(q * 0.6, shape_func)
    
    def analyze_differences(self, load_intensity=1000.0):
        """同一荷重下での形状性能比較"""
        
        # 最適化形状に実荷重適用
        w_opt, curv_opt, stress_opt = self.optimized_shape_under_load(load_intensity)
        
        # 従来形状に同一荷重適用
        w_conv, curv_conv, stress_conv = self.loaded_beam_response(load_intensity)
        
        # スケーリング不要（同一荷重条件のため）
        print(f"\n🔍 同一荷重条件での比較:")
        print(f"   荷重強度: {load_intensity} N or N/m")
        print(f"   最適化形状最大変位: {np.max(np.abs(w_opt))*1000:.2f} mm")
        print(f"   従来形状最大変位: {np.max(np.abs(w_conv))*1000:.2f} mm")
        
        # 性能比較計算
        max_stress_opt = np.max(np.abs(stress_opt))
        max_stress_conv = np.max(np.abs(stress_conv))
        max_deflection_opt = np.max(np.abs(w_opt))
        max_deflection_conv = np.max(np.abs(w_conv))
        
        # 性能指標
        performance_metrics = {
            'deflection_reduction': (max_deflection_conv - max_deflection_opt) / max_deflection_conv * 100,
            'stress_reduction': (max_stress_conv - max_stress_opt) / max_stress_conv * 100,
            'deflection_ratio': max_deflection_opt / max_deflection_conv,
            'stress_ratio': max_stress_opt / max_stress_conv,
            'stiffness_improvement': max_deflection_conv / max_deflection_opt,
            'strength_improvement': max_stress_conv / max_stress_opt,
            'material_efficiency': (max_stress_conv / max_stress_opt) / 1.0,  # 同一材料量仮定
            'smoothness_opt': np.std(np.gradient(curv_opt)),
            'smoothness_conv': np.std(np.gradient(curv_conv))
        }
        
        return {
            'optimized': (w_opt, curv_opt, stress_opt),
            'conventional': (w_conv, curv_conv, stress_conv),
            'performance': performance_metrics
        }
    
    def create_comparison_plot(self, load_intensity=1000.0):
        """比較プロットを作成"""
        
        results = self.analyze_differences(load_intensity)
        w_opt, curv_opt, stress_opt = results['optimized']
        w_conv, curv_conv, stress_conv = results['conventional'] 
        perf = results['performance']
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle(f'Shape Performance Comparison Under {self.load_case.title()} Load', fontsize=16, fontweight='bold')
        
        # 1. 変位比較
        ax1 = axes[0, 0]
        ax1.plot(self.x, w_opt*1000, 'b-', linewidth=2, label='Optimized Shape')
        ax1.plot(self.x, w_conv*1000, 'r--', linewidth=2, label='Conventional Shape')
        ax1.set_xlabel('Position (mm)')
        ax1.set_ylabel('Deflection (mm)')
        ax1.set_title(f'Deflection Under {load_intensity} N Load')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. 曲率比較
        ax2 = axes[0, 1]
        ax2.plot(self.x, curv_opt*1e6, 'b-', linewidth=2, label='Optimized Curvature')
        ax2.plot(self.x, curv_conv*1e6, 'r--', linewidth=2, label='Conventional Curvature')
        ax2.set_xlabel('Position (mm)')
        ax2.set_ylabel('Curvature (x10^-6 m^-1)')
        ax2.set_title('Curvature Distribution Comparison')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. 応力比較
        ax3 = axes[1, 0]
        ax3.plot(self.x, stress_opt/1e6, 'b-', linewidth=2, label='Optimized Stress')
        ax3.plot(self.x, stress_conv/1e6, 'r--', linewidth=2, label='Conventional Stress')
        ax3.axhline(y=0, color='k', linestyle='-', alpha=0.3)
        ax3.set_xlabel('Position (mm)')
        ax3.set_ylabel('Stress (MPa)')
        ax3.set_title('Stress Distribution Comparison')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. 性能指標
        ax4 = axes[1, 1]
        metrics = ['Deflection\nReduction %', 'Stress\nReduction %', 'Stiffness\nImprovement', 'Strength\nImprovement']
        values = [
            perf['deflection_reduction'],
            perf['stress_reduction'],
            perf['stiffness_improvement'],
            perf['strength_improvement']
        ]
        
        # 負の値の色分け
        colors = ['green' if v > 0 else 'red' for v in values]
        bars = ax4.bar(range(len(metrics)), values, color=colors)
        ax4.set_xticks(range(len(metrics)))
        ax4.set_xticklabels(metrics, rotation=45, ha='right')
        ax4.set_title('Shape Performance Comparison')
        ax4.axhline(y=0, color='k', linestyle='-', alpha=0.5)
        ax4.grid(True, alpha=0.3, axis='y')
        
        # 値を棒グラフ上に表示
        for bar, val in zip(bars, values):
            y_pos = bar.get_height() + (0.1 if val > 0 else -0.2)
            ax4.text(bar.get_x() + bar.get_width()/2, y_pos,
                    f'{val:.1f}', ha='center', va='bottom' if val > 0 else 'top')
        
        plt.tight_layout()
        
        # 性能結果を表示
        print(f"\n📈 Shape Performance Analysis Results:")
        print(f"   Deflection Reduction: {perf['deflection_reduction']:.1f}%")
        print(f"   Stress Reduction: {perf['stress_reduction']:.1f}%")
        print(f"   Stiffness Improvement: {perf['stiffness_improvement']:.2f}x")
        print(f"   Strength Improvement: {perf['strength_improvement']:.2f}x")
        print(f"   Material Efficiency: {perf['material_efficiency']:.2f}")
        
        # 性能評価
        if perf['deflection_reduction'] > 10:
            print("   ✅  Optimized shape shows significant deflection reduction")
        elif perf['deflection_reduction'] < -10:
            print("   ⚠️  Optimized shape has higher deflection")
        
        if perf['stress_reduction'] > 10:
            print("   ✅  Optimized shape shows significant stress reduction")
        elif perf['stress_reduction'] < -10:
            print("   ⚠️  Optimized shape has higher stress")
        
        return fig, results

def main():
    """メイン実行関数"""
    print("=" * 60)
    print("Shape Performance Comparison Under Same Load Conditions")
    print("Optimized Shape vs Conventional Shape Analysis")
    print("=" * 60)
    
    # 異なる荷重ケースでの比較
    load_cases = ['uniform', 'point']
    
    for i, load_case in enumerate(load_cases):
        print(f"\n{'='*20} Case {i+1}: {load_case} loading {'='*20}")
        
        # 比較オブジェクト作成
        beam_comp = BeamComparison(
            length=1000.0,      # 1m はり
            E=210e9,           # 鋼材のヤング率  
            I=8.33e-6,         # 50×100mm断面相当
            load_case=load_case
        )
        
        # 比較プロット作成
        fig, results = beam_comp.create_comparison_plot(load_intensity=1000.0)
        
        # プロット保存
        filename = f"shape_performance_{load_case}_loading.png"
        fig.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"   Plot saved: {filename}")
    
    plt.show()

if __name__ == "__main__":
    main()