#define _CRT_SECURE_NO_WARNINGS
#include <iostream>
#include <string>
#include <opencv2/opencv.hpp>
std::string win_src = "src";
std::string win_dst = "dst";

int main()
{
  cv::Mat img_src = cv::imread("./01-06.jpg", 1);
  cv::Mat img_gray, img_dst;

  if (!img_src.data) {
    std::cout << "error" << std::endl;
    return -1;
  }

  cv::cvtColor(img_src, img_gray, cv::COLOR_BGR2GRAY);
  img_src.copyTo(img_dst);

  std::vector<cv::Point2f> corners;
  cv::goodFeaturesToTrack(img_gray, corners, 1000, 0.1, 5);
  for (int i = 0; i < corners.size(); i++) {
    cv::circle(img_dst, cv::Point(corners[i].x, corners[i].y), 3, cv::Scalar(0, 0, 255), 2);
  }

  // ウインドウ生成
  cv::namedWindow(win_src, cv::WINDOW_AUTOSIZE);
  cv::namedWindow(win_dst, cv::WINDOW_AUTOSIZE);

  // 表示
  cv::imshow(win_src, img_src);
  cv::imshow(win_dst, img_dst);

  cv::waitKey(0);

  return 0;
}
