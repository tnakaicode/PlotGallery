#define _CRT_SECURE_NO_WARNINGS
#include <iostream>
#include <opencv2/opencv.hpp>
#include <opencv2/stitching.hpp>

int main()
{
  cv::Mat img_dst;
  std::vector< cv::Mat > img_src;

  img_src.push_back(cv::imread("05-08-a.jpg"));
  img_src.push_back(cv::imread("05-08-b.jpg"));
  img_src.push_back(cv::imread("05-08-c.jpg"));
  img_src.push_back(cv::imread("05-08-d.jpg"));
  img_src.push_back(cv::imread("05-08-e.jpg"));
  img_src.push_back(cv::imread("05-08-f.jpg"));

  cv::Stitcher stitcher = cv::Stitcher::createDefault();
  cv::Stitcher::Status status = stitcher.stitch(img_src, img_dst);

  if (status == cv::Stitcher::OK) cv::imshow("dst", img_dst);
  else std::cout << "failed" << std::endl;

  cv::waitKey(0);

  return 0;
}