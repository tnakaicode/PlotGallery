#define _CRT_SECURE_NO_WARNINGS
#define _USE_MATH_DEFINES //M_PIを使用するために必要
#include <iostream>
#include <fstream>
#include <cmath>
#include <ctime>
#include <opencv2/opencv.hpp>

int main()
{
  int num_data = 200; //各クラスのデータ総数
  cv::Mat class1(num_data, 2, CV_64FC1); //クラス1のデータ保存用
  cv::Mat class2(num_data, 2, CV_64FC1); //クラス2のデータ保存用
  cv::Mat labels(2 * num_data, 1, CV_32SC1); //クラスのラベル値保存用
  std::ofstream fout;

  //乱数生成器を初期化．
  cv::RNG rng((unsigned int)time(NULL));
  //人工的データの生成
  for (int i = 0; i < num_data; i++) {
    class1.at<double>(i, 0) = rng.gaussian(0.5); //x(平均値0)
    class1.at<double>(i, 1) = rng.gaussian(0.5); //y(平均値0)

    class2.at<double>(i, 0) = rng.gaussian(2.0) + 5.0; //x(平均値5.0)
    class2.at<double>(i, 1) = rng.gaussian(2.0) + 1.0; //y(平均値1.0)
  }
  for (int i = 0; i < 2 * num_data; i++) {
    if (i < num_data) labels.at<int>(i) = 0; //前半クラス1のラベル値
    else labels.at<int>(i) = 1; //後半クラス2のラベル値
  }

  //人工的データの保存
  fout.open("data.txt");
  if (!fout.is_open()) {
    std::cerr << "ERR: fout open" << std::endl;
    return -1;
  }

  for (int i = 0; i < num_data; i++) {
    fout << class1.at<double>(i, 0) << " " << class1.at<double>(i, 1) << " " << labels.at<int>(i) << std::endl;
  }
  for (int i = 0; i < num_data; i++) {
    fout << class2.at<double>(i, 0) << " " << class2.at<double>(i, 1) << " " << labels.at<int>(i + num_data) << std::endl;
  }

  fout.close();

  system("PAUSE");
  return 0;
}
