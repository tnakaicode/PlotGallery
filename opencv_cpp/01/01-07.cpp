#define _CRT_SECURE_NO_WARNINGS
#include <iostream>
#include <string>
#include <opencv2/opencv.hpp>
std::string win_src = "src";
std::string win_edge = "edge";
std::string win_dst = "dst";

int main()
{
  cv::Mat img_src = cv::imread("./01-13.jpg", 1);
  cv::Mat img_gray, img_edge, img_dst;

  if (!img_src.data) {
    std::cout << "error" << std::endl;
    return -1;
  }

  img_src.copyTo(img_dst);

  cv::cvtColor(img_src, img_gray, cv::COLOR_BGR2GRAY);

  // Canny
  cv::Canny(img_gray, img_edge, 80, 120);

  std::vector<cv::Vec3f> circles;
  cv::HoughCircles(img_edge, circles, cv::HOUGH_GRADIENT, 50, 100);

  for (int i = 0; i < circles.size(); i++) {
    cv::Point center((int)circles[i][0], (int)circles[i][1]);
    int radius = (int)circles[i][2];
    cv::circle(img_dst, center, radius, cv::Scalar(0, 0, 255), 3);
  }

  // ウインドウ生成
  cv::namedWindow(win_src, cv::WINDOW_AUTOSIZE);
  cv::namedWindow(win_dst, cv::WINDOW_AUTOSIZE);

  // 表示
  cv::imshow(win_src, img_src);
  cv::imshow(win_edge, img_edge);
  cv::imshow(win_dst, img_dst);

  cv::waitKey(0);

  return 0;
}
