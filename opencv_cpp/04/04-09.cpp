#define _CRT_SECURE_NO_WARNINGS
#include <iostream>
#include <opencv2/opencv.hpp>

int main()
{
  cv::VideoCapture cap("%06d.png");

  while (1) {
    cv::Mat img_src;
    cap >> img_src;
    cv::imshow("src", img_src);
    if (cv::waitKey(10) == 'q') break;
  }
  return 0;
}
