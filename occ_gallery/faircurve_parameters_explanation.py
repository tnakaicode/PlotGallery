#!/usr/bin/env python

"""
FairCurve_MinimalVariation パラメータ説明とデモ
各Set***メソッドの意味、効果、適切な設定値について詳しく解説
"""

import math
from OCC.Core.gp import gp_Pnt2d
from OCC.Core.FairCurve import FairCurve_MinimalVariation


def explain_faircurve_parameters():
    """FairCurveの各パラメータの詳細説明"""

    print("=" * 80)
    print("FairCurve_MinimalVariation パラメータ詳細説明")
    print("=" * 80)

    print("\n1. コンストラクタパラメータ:")
    print("   FairCurve_MinimalVariation(P1, P2, Height, Slope)")
    print("   - P1, P2: 始点と終点の2D座標")
    print("   - Height: バッテンの厚み（曲がりにくさを表現）")
    print("   - Slope: 初期傾斜パラメータ（変形の度合い）")

    print("\n2. 制約次数設定:")
    print("   SetConstraintOrder1/2(order)")
    print("   - order=0: 点のみ拘束（位置固定）")
    print("   - order=1: 点+接線拘束（位置と接線方向固定）")
    print("   - order=2: 点+接線+曲率拘束（位置、接線、曲率固定）")
    print("   推奨: 大変形時は1、小変形時は2")

    print("\n3. 角度設定:")
    print("   SetAngle1/2(angle)")
    print("   - angle: 端点での接線角度（ラジアン）")
    print("   - 正の値で上向き、負の値で下向き")
    print("   - 例: math.radians(10) = 10度上向き")

    print("\n4. 曲率設定:")
    print("   SetCurvature1/2(curvature)")
    print("   - curvature: 端点での曲率値（1/半径）")
    print("   - 正の値で上に凸、負の値で下に凸")
    print("   - 推奨値: slope / (length * 0.25)")

    print("\n5. 物理比率設定:")
    print("   SetPhysicalRatio(ratio)")
    print("   - ratio: 材料の剛性比（0.01 ～ 1.0の範囲）")
    print("   - 高い値: より剛い材料（変形しにくい）")
    print("   - 低い値: より柔らかい材料（変形しやすい）")

    print("\n6. 自由滑動設定:")
    print("   SetFreeSliding(bool)")
    print("   - True: 端点が自由に滑る（より自然な変形）")
    print("   - False: 端点固定（より制限された変形）")
    print("   - 推奨: 通常はTrue")

    print("\n7. 滑動係数設定:")
    print("   SetSlidingFactor(factor)")
    print("   - factor: 変形の滑らかさ（0.5 ～ 3.0程度）")
    print("   - 高い値: より滑らかな変形")
    print("   - 低い値: よりシャープな変形")


def demo_parameter_effects():
    """各パラメータの効果をデモンストレーション"""

    print("\n" + "=" * 80)
    print("パラメータ効果デモ")
    print("=" * 80)

    # 基本設定
    pt1 = gp_Pnt2d(0.0, 0.0)
    pt2 = gp_Pnt2d(100.0, 0.0)
    height = 10.0
    slope = 0.01

    print(f"\n基本設定: 長さ100mm, 高さ{height}, 傾斜{slope}")

    # 1. 制約次数の効果
    print("\n--- 制約次数の効果 ---")
    for order in [1, 2]:
        fc = FairCurve_MinimalVariation(pt1, pt2, height, slope)
        fc.SetConstraintOrder1(order)
        fc.SetConstraintOrder2(order)
        fc.SetAngle1(math.radians(10))
        fc.SetAngle2(math.radians(-10))
        fc.SetFreeSliding(True)

        # 適切な曲率設定
        curvature = slope / 25.0
        fc.SetCurvature1(curvature)
        fc.SetCurvature2(-curvature)

        # 物理比率設定
        fc.SetPhysicalRatio(0.1)
        fc.SetSlidingFactor(1.0)

        status = fc.Compute()
        print(f"  制約次数 {order}: ステータス = {status}")

    # 2. 角度の効果
    print("\n--- 角度の効果 ---")
    for angle_deg in [0, 10, 20, 30]:
        fc = FairCurve_MinimalVariation(pt1, pt2, height, slope)
        fc.SetConstraintOrder1(1)
        fc.SetConstraintOrder2(1)

        angle_rad = math.radians(angle_deg)
        fc.SetAngle1(angle_rad)
        fc.SetAngle2(-angle_rad)
        fc.SetFreeSliding(True)

        curvature = slope / 25.0
        fc.SetCurvature1(curvature)
        fc.SetCurvature2(-curvature)
        fc.SetPhysicalRatio(0.1)
        fc.SetSlidingFactor(1.0)

        status = fc.Compute()
        print(f"  角度 ±{angle_deg}度: ステータス = {status}")

    # 3. 物理比率の効果
    print("\n--- 物理比率の効果 ---")
    for ratio in [0.01, 0.05, 0.1, 0.5, 1.0]:
        fc = FairCurve_MinimalVariation(pt1, pt2, height, slope)
        fc.SetConstraintOrder1(1)
        fc.SetConstraintOrder2(1)
        fc.SetAngle1(math.radians(10))
        fc.SetAngle2(math.radians(-10))
        fc.SetFreeSliding(True)

        curvature = slope / 25.0
        fc.SetCurvature1(curvature)
        fc.SetCurvature2(-curvature)

        try:
            fc.SetPhysicalRatio(ratio)
            fc.SetSlidingFactor(1.0)
            status = fc.Compute()
            print(f"  物理比率 {ratio}: ステータス = {status}")
        except RuntimeError as e:
            print(f"  物理比率 {ratio}: エラー - {str(e)}")

    # 4. 滑動係数の効果
    print("\n--- 滑動係数の効果 ---")
    for factor in [0.5, 1.0, 1.5, 2.0, 3.0]:
        fc = FairCurve_MinimalVariation(pt1, pt2, height, slope)
        fc.SetConstraintOrder1(1)
        fc.SetConstraintOrder2(1)
        fc.SetAngle1(math.radians(10))
        fc.SetAngle2(math.radians(-10))
        fc.SetFreeSliding(True)

        curvature = slope / 25.0
        fc.SetCurvature1(curvature)
        fc.SetCurvature2(-curvature)
        fc.SetPhysicalRatio(0.1)
        fc.SetSlidingFactor(factor)

        status = fc.Compute()
        print(f"  滑動係数 {factor}: ステータス = {status}")


def best_practices():
    """FairCurveの最良の実践方法"""

    print("\n" + "=" * 80)
    print("FairCurve 最良の実践方法")
    print("=" * 80)

    print("\n1. パラメータ設定の順序:")
    print("   1) 基本形状: P1, P2, Height, Slope")
    print("   2) 制約次数: SetConstraintOrder1/2")
    print("   3) 角度: SetAngle1/2")
    print("   4) 自由滑動: SetFreeSliding")
    print("   5) 曲率: SetCurvature1/2")
    print("   6) 物理比率: SetPhysicalRatio")
    print("   7) 滑動係数: SetSlidingFactor")
    print("   8) 計算実行: Compute()")

    print("\n2. 推奨値の計算式:")
    print("   - Height: sqrt(bending_rigidity / 1e6)")
    print("   - Slope: deflection / length")
    print("   - Curvature: slope / (length * 0.25)")
    print("   - PhysicalRatio: bending_rigidity / 1e7 (0.01-1.0に制限)")
    print("   - SlidingFactor: 1.0 + slope (0.5-3.0に制限)")

    print("\n3. トラブルシューティング:")
    print("   - 収束しない場合: 制約次数を1に下げる")
    print("   - 不自然な形状: PhysicalRatioを調整")
    print("   - 計算エラー: パラメータ範囲を確認")
    print("   - 変形が小さすぎる: Heightを下げる")
    print("   - 変形が大きすぎる: Heightを上げる")

    print("\n4. 物理的意味:")
    print("   - Height ≈ 材料の曲げ剛性")
    print("   - Slope ≈ 最大変位/長さ比")
    print("   - Curvature ≈ 端部の曲率半径")
    print("   - PhysicalRatio ≈ 材料の硬さ")
    print("   - Angle ≈ 境界条件での接線角")


if __name__ == "__main__":
    explain_faircurve_parameters()
    demo_parameter_effects()
    best_practices()

    print("\n" + "=" * 80)
    print("説明完了")
    print("=" * 80)
