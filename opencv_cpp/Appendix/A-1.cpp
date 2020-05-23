#define _CRT_SECURE_NO_WARNINGS
#define _USE_MATH_DEFINES
#include <iostream>
#include <string>
#include <cmath>
#include <opencv2/opencv.hpp>
std::string win_src = "src";

int main()
{
  // 640x480pixelの黒い画像
  cv::Mat img_src = cv::Mat::zeros(cv::Size(640, 480), CV_8UC3);

  // ウインドウ生成
  cv::namedWindow(win_src, cv::WINDOW_AUTOSIZE);

  // 点(0, 0)と点(640, 480)を結ぶ太さ5の黄色の線分
  line(img_src, cv::Point(0, 0), cv::Point(640, 480), cv::Scalar(0, 255, 255), 5);

  // 中心座標(320, 240)，半径100，太さ3の青色の円
  cv::circle(img_src, cv::Point(320, 240), 100, cv::Scalar(255, 0, 0), 3);

  // 中心座標(500, 100)，半径50，塗りつぶしの緑色の円
  cv::circle(img_src, cv::Point(500, 100), 50, cv::Scalar(0, 255, 0), -1);

  // 左上座標(100, 150)，幅50，高さ150，太さ2の赤色の矩形
  cv::rectangle(img_src, cv::Rect(100, 150, 50, 150), cv::Scalar(0, 0, 255), 2);

  // 左上座標(50, 350)，幅200，高さ50，塗りつぶしの紫色の矩形
  cv::rectangle(img_src, cv::Rect(50, 350, 200, 50), cv::Scalar(255, 0, 255), -1);

  // 左下座標(300, 450), 倍率3，太さ5の水色の文字列123
  cv::putText(img_src, "123", cv::Point(300, 450), 0, 3, cv::Scalar(255, 255, 0), 5);

  // 表示
  cv::imshow(win_src, img_src);

  // キー入力待ち
  cv::waitKey(0);

  return 0;
}