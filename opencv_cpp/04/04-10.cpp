#define _CRT_SECURE_NO_WARNINGS
#include <iostream>
#include <string>
#include <opencv2/opencv.hpp>
#include <opencv2/tracking.hpp>

int main()
{
  cv::Mat img_src;
  cv::VideoCapture cap(0);

  std::vector<std::string> method;
  method.push_back("MIL"); // Multiple Instance Learning
  method.push_back("TLD"); // Tracking-learning-detection
  method.push_back("MEDIANFLOW");
  method.push_back("BOOSTING");
  method.push_back("KCF"); // Kernelized Correlation Filters

  // トラッキング手法を選択
  cv::Ptr<cv::Tracker> tracker = cv::Tracker::create(method[4]);

  // 追跡範囲をマウスで選択して，Enter
  cap >> img_src;
  cv::Rect2d roi = cv::selectROI(img_src, false);

  tracker->init(img_src, roi); // 初期化

  while (1) {
    cap >> img_src;
    tracker->update(img_src, roi); // 物体追跡
    cv::rectangle(img_src, roi, cv::Scalar(0, 0, 255));
    cv::imshow("result", img_src);
    if (cv::waitKey(1) == 'q') break;
  }
  return 0;
}