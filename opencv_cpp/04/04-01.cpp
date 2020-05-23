#define _CRT_SECURE_NO_WARNINGS
#include <iostream>
#include <string>
#include <opencv2/opencv.hpp>
std::string win_src = "src";
std::string win_template = "template";
std::string win_minmax = "minmax";
std::string win_dst = "dst";

int main()
{
  cv::Mat img_src = cv::imread("./04-02-a.jpg", 1);
  cv::Mat img_template = cv::imread("./04-02-b.jpg", 1);
  cv::Mat img_minmax, img_dst;

  if (!img_src.data || !img_template.data) {
    std::cout << "error" << std::endl;
    return -1;
  }

  img_src.copyTo(img_dst);

  // テンプレートマッチング
  cv::matchTemplate(img_src, img_template, img_minmax, cv::TM_CCOEFF_NORMED);

  // 最大位置に矩形描画
  cv::Point min_pt, max_pt;
  double min_val, max_val;
  cv::minMaxLoc(img_minmax, &min_val, &max_val, &min_pt, &max_pt);
  cv::rectangle(img_dst, cv::Rect(max_pt.x, max_pt.y, img_template.cols, img_template.rows), cv::Scalar(255, 255, 255), 10);

  // ウインドウ生成
  cv::namedWindow(win_src, cv::WINDOW_AUTOSIZE);
  cv::namedWindow(win_template, cv::WINDOW_AUTOSIZE);
  cv::namedWindow(win_minmax, cv::WINDOW_AUTOSIZE);
  cv::namedWindow(win_dst, cv::WINDOW_AUTOSIZE);

  // 表示
  cv::imshow(win_src, img_src);
  cv::imshow(win_template, img_template);
  cv::imshow(win_minmax, img_minmax);
  cv::imshow(win_dst, img_dst);

  cv::waitKey(0);

  return 0;
}
