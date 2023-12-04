#import pypcd
from pypcd.pypcd import PointCloud
# also can read from file handles.
pc = PointCloud.from_path('./assets/models/bunny.pcd')
# pc.pc_data has the data as a structured array
# pc.fields, pc.count, etc have the metadata

# center the x field
pc.pc_data['x'] -= pc.pc_data['x'].mean()

# save as binary compressed
# pc.save_pcd('bar.pcd', compression='binary_compressed')

import open3d
import numpy as np
import copy

def preprocess_point_cloud(pointcloud, voxel_size):
    # Keypoint を Voxel Down Sample で生成
    keypoints = open3d.voxel_down_sample(pointcloud, voxel_size)

    # 法線推定
    radius_normal = voxel_size * 2
    view_point = np.array([0., 10., 10.], dtype="float64")
    open3d.estimate_normals(
        keypoints,
        search_param = open3d.KDTreeSearchParamHybrid(radius = radius_normal, max_nn = 30))
    open3d.orient_normals_towards_camera_location(keypoints, camera_location = view_point)

    #　FPFH特徴量計算
    radius_feature = voxel_size * 5
    fpfh = open3d.compute_fpfh_feature(
        keypoints,
        search_param = open3d.KDTreeSearchParamHybrid(radius = radius_feature, max_nn = 100))

    return keypoints, fpfh

# 読み込み
scene1 = open3d.read_point_cloud("scene1.ply")
# scene2 = open3d.read_point_cloud("scene2.ply")

# scene2 を適当に回転・並進
transform_matrix = np.asarray([
    [1., 0., 0., -0.1],
    [0., 0., -1., 0.1],
    [0., 1., 0., -0.1],
    [0., 0., 0., 1.]], dtype="float64")

# 位置合わせ前の点群の表示
# draw_registration_result(scene1, scene2, np.eye(4))

voxel_size = 0.01

# RANSAC による Global Registration
scene1_kp, scene1_fpfh = preprocess_point_cloud(scene1, voxel_size)
