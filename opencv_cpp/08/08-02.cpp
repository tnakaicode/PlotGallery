#define _CRT_SECURE_NO_WARNINGS
#include <iostream>
#include <opencv2/opencv.hpp>

int main()
{
  // ウィンドウ名やファイル名に関するパラメータ
  const std::string  win_src = "Source";
  const std::string  win_und = "Undistorted Image";
  const std::string  file_cam_param = "cam_param.xml";

  // チェッカーパターンに関する変数とパラメータ
  std::vector<cv::Mat>  img;			// チェッカーパターン画像
  const int             NUM_IMG = 5;	// チェッカーパターンが何枚あるか
  const cv::Size        PAT_SIZE(10, 7);			// チェッカーパターンの交点の数
  float                 CHESS_SIZE = 24.0;			// チェッカーパターンのマス目のサイズ [mm]

  // 座標に関する変数
  std::vector<std::vector<cv::Point3f> >  obj_pos(NUM_IMG);	// チェッカー交点座標と対応する世界座標の値を格納する行列
  std::vector<std::vector<cv::Point2f> >  img_pos(NUM_IMG);	// チェッカー交点座標を格納する行列

  // カメラキャリブレーションのパラメータ
  cv::TermCriteria  criteria(cv::TermCriteria::MAX_ITER | cv::TermCriteria::EPS, 20, 0.001);

  // カメラパラメータ行列
  cv::Mat               inner;		// 内部パラメータ行列
  cv::Mat               distort;      // レンズ歪み行列
  std::vector<cv::Mat>  r_vec;		// 撮影画像ごとに得られる回転ベクトル
  std::vector<cv::Mat>  t_vec;		// 撮影画像ごとに得られる平行移動ベクトル

  // (1) キャリブレーションパターンの読み込み
  for (int i = 0; i < NUM_IMG; i++) {
    std::string	fileName = "./calib_img" + std::to_string(i + 1) + ".jpg";
    img.push_back(cv::imread(fileName));
  }

  // (2) 3次元空間座標での交点位置の設定
  for (int i = 0; i < NUM_IMG; i++) {
    for (int j = 0; j < PAT_SIZE.area(); j++) {
      obj_pos[i].push_back(
        cv::Point3f(static_cast<float>(j % PAT_SIZE.width * CHESS_SIZE),
          static_cast<float>(j / PAT_SIZE.width * CHESS_SIZE),
          0.0));
    }
  }

  // (3) チェスボード（キャリブレーションパターン）のコーナー検出
  for (int i = 0; i < NUM_IMG; i++) {
    std::cout << "calib_img" << i + 1 << ".jpg";
    cv::imshow(win_src, img[i]);
    if (cv::findChessboardCorners(img[i], PAT_SIZE, img_pos[i])) {
      cv::drawChessboardCorners(img[i], PAT_SIZE, img_pos[i], true);
      cv::imshow(win_src, img[i]);
      std::cout << " - success" << std::endl;
      cv::waitKey(0);
    }
    else {
      std::cout << " - fail" << std::endl;
      cv::waitKey(0);
      return -1;
    }
  }

  // (4) Zhangの手法によるキャリブレーション
  cv::calibrateCamera(obj_pos, img_pos, img[0].size(), inner, distort, r_vec, t_vec);

  // (5) 回転ベクトルと平行移動ベクトルを4x4の外部パラメータ行列に書き換え(1枚目の外部パラメータ行列のみ出力)
  cv::Mat	extr(4, 4, CV_64F);
  cv::setIdentity(extr);
  cv::Rodrigues(r_vec[0], extr(cv::Rect(0, 0, 3, 3))); // 回転ベクトルの変換
  t_vec[0].copyTo(extr(cv::Rect(3, 0, 1, 3))); // 並進ベクトルの変換

  // (6) xmlファイルへの書き出し
  cv::FileStorage	fswrite(file_cam_param, cv::FileStorage::WRITE);
  if (fswrite.isOpened()) {
    fswrite << "extrinsic" << extr;
    fswrite << "intrinsic" << inner;
    fswrite << "distortion" << distort;
  }
  fswrite.release();

  // (7) 画像の歪み補正
  cv::Mat	img_undist;
  for (int i = 0; i < NUM_IMG; i++) {
    cv::undistort(img[i], img_undist, inner, distort);
    cv::imshow(win_src, img[i]);
    cv::imshow(win_und, img_undist);
    cv::waitKey(0);
  }

  return 0;
}