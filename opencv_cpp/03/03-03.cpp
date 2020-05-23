#define _CRT_SECURE_NO_WARNINGS
#include <iostream>
#include <string>
#include <opencv2/opencv.hpp>

// フローの表示間隔
#define FLOW_W (10)
#define FLOW_H (10)

std::string win_src = "opticalflow";

int main()
{
  cv::Mat img_pre, img_now;
  cv::Mat img_pre_g, img_now_g;
  cv::Mat flow;

  img_pre = cv::imread("03-02-a.jpg", 1);
  img_now = cv::imread("03-02-b.jpg", 1);
  cv::cvtColor(img_pre, img_pre_g, cv::COLOR_BGR2GRAY);
  cv::cvtColor(img_now, img_now_g, cv::COLOR_BGR2GRAY);

  // フロー計算
  cv::calcOpticalFlowFarneback(img_pre_g, img_now_g, flow, 0.5, 3, 30, 3, 3, 1.1, 0);

  // フロー描画
  for (int y = 0; y < img_now.rows; y += FLOW_H) {
    for (int x = 0; x < img_now.cols; x += FLOW_W) {
      cv::Point2f ps = cv::Point2f(x, y);
      cv::Point2f pe = ps + flow.at<cv::Point2f>(y, x);
      cv::arrowedLine(img_now, ps, pe, cv::Scalar(0, 0, 255), 1, 8, 0, 1.0);
    }
  }

  // 表示
  cv::namedWindow(win_src);
  cv::imshow(win_src, img_now);

  cv::waitKey(0);

  return 0;
}
