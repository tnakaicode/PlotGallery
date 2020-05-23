#define _CRT_SECURE_NO_WARNINGS
#include <opencv2/opencv.hpp>
#include <opencv2/sfm.hpp>

int main()
{
  // カメラの内部パラメータに関する変数（キャリブレーションした値を入れる）
  float  f = 1094.0;	// 焦点距離 
  float  cx = 491.0;	// 画像中心(x) pixel
  float  cy = 368.0;	// 画像中心(y) pixel

  // 入力画像に関する変数
  const int        NUM_IMG = 5;	//入力画像の数
  std::vector<std::string>   image_files; //入力画像のファイル名（サンプルではカレントディレクトリにあるとする）

  // (1)入力ファイル名のセット
  for (int i = 0; i < NUM_IMG; i++)
    image_files.push_back("09-06-" + std::to_string(i + 1) + ".jpg");

  // (2)内部パラメータ行列の生成
  cv::Matx33d K = cv::Matx33d(f, 0, cx,
    0, f, cy,
    0, 0, 1);

  // (3)SfMモジュールを用いた複数の画像データからの３次元再構成（点群が計算される）
  bool is_projective = true;
  std::vector<cv::Mat> Rs_est, ts_est, points3d_estimated;
  cv::sfm::reconstruct(image_files, Rs_est, ts_est, K, points3d_estimated, is_projective);

  // (4)結果の表示(Vizを使用する）
  //...Windowを生成
  cv::viz::Viz3d window("Coordinate Frame");
  window.setWindowSize(cv::Size(800, 600));
  window.setBackgroundColor(); // 指定しないと背景は黒

  //...推定された３次元位置をセット
  std::vector<cv::Vec3f> point_cloud_est;
  for (int i = 0; i < points3d_estimated.size(); ++i)
    point_cloud_est.push_back(cv::Vec3f(points3d_estimated[i]));

  //...カメラ位置のセット
  std::vector<cv::Affine3d> path;
  for (size_t i = 0; i < Rs_est.size(); ++i)
    path.push_back(cv::Affine3d(Rs_est[i], ts_est[i]).inv());

  //...３次元座標（点での）の表示
  cv::viz::WCloud cloud_widget(point_cloud_est, cv::viz::Color::green());
  window.showWidget("point_cloud", cloud_widget);

  //...カメラ位置の表示
  window.showWidget("cameras_frames_and_lines", cv::viz::WTrajectory(path, cv::viz::WTrajectory::BOTH, 0.1, cv::viz::Color::green()));
  window.showWidget("cameras_frustums", cv::viz::WTrajectoryFrustums(path, K, 0.1, cv::viz::Color::yellow()));
  window.setViewerPose(path[0]);

  //...'q'を押すとプログラム終了
  std::cout << std::endl << "Press 'q' to close each windows ... " << std::endl;
  window.spin();

  return 0;
}
