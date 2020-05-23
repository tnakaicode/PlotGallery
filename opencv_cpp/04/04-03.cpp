#define _CRT_SECURE_NO_WARNINGS
#include <iostream>
#include <string>
#include <opencv2/opencv.hpp>
std::string win_src = "src";
std::string win_bin = "bin";

int main()
{
  cv::Mat img_src, img_bin;
  cv::Rect rct;
  cv::VideoCapture cap(0);

  if (!cap.isOpened()) {
    std::cout << "camera open error" << std::endl;
    return -1;
  }

  // 画面左上に初期ウインドウを設定
  cap >> img_src;
  int div = 5;
  rct.x = 0;
  rct.y = 0;
  rct.width = img_src.cols / div;
  rct.height = img_src.rows / div;

  // ウインドウ生成
  cv::namedWindow(win_src, cv::WINDOW_AUTOSIZE);
  cv::namedWindow(win_bin, cv::WINDOW_AUTOSIZE);

  // 終了条件　最大繰返回数10，または最小移動距離1ピクセル以下
  cv::TermCriteria cri(cv::TermCriteria::COUNT + cv::TermCriteria::EPS, 10, 1);

  while (1) {
    std::vector<cv::Mat> vec_bgr(3);
    int ret;
    int th = 220;

    cap >> img_src;

    cv::split(img_src, vec_bgr); // RGB分離
    cv::threshold(vec_bgr[2], img_bin, th, 255, cv::THRESH_BINARY); // 二値化

    ret = cv::meanShift(img_bin, rct, cri); //meanshift
    cv::rectangle(img_src, rct, cv::Scalar(255, 0, 0), 3); // 結果を矩形で描画

    cv::imshow(win_src, img_src);
    cv::imshow(win_bin, img_bin);

    if (cv::waitKey(10) == 'q') break;
  }

  return 0;
}
