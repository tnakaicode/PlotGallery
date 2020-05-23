#define _CRT_SECURE_NO_WARNINGS
#include <iostream>
#include <vector>
#include <opencv2/opencv.hpp>

int main()
{
  cv::Mat img_src1, img_src2, img_dst;
  std::vector<cv::KeyPoint> kpts1, kpts2;
  cv::Mat desc1, desc2;

  // 画像の読み込み
  img_src1 = cv::imread("02-02-a.jpg", 0);
  img_src2 = cv::imread("02-02-b.jpg", 0);

  // 特徴量記述の指定
  cv::Ptr<cv::KAZE> detector = cv::KAZE::create(); // KAZE
  //cv::Ptr<cv::AKAZE> detector = cv::AKAZE::create(); // AKAZE

  // 特徴点の検出，特徴量の算出
  detector->detectAndCompute(img_src1, cv::noArray(), kpts1, desc1);
  detector->detectAndCompute(img_src2, cv::noArray(), kpts2, desc2);

  // 特徴点の対応付け
  cv::Ptr<cv::DescriptorMatcher> matcher = cv::DescriptorMatcher::create("BruteForce");
  std::vector<cv::DMatch> matches;
  matcher->match(desc1, desc2, matches);

  // 特徴点の対応を表示
  cv::drawMatches(img_src1, kpts1, img_src2, kpts2, matches, img_dst);
  cv::imshow("dst", img_dst);
  cv::waitKey(0);

  return 0;
}