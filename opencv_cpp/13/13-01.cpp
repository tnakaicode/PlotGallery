#define _CRT_SECURE_NO_WARNINGS
#define _USE_MATH_DEFINES
#include <iostream>
#include <fstream>
#include <cmath>
#include <ctime>
#include <opencv2/opencv.hpp>

int main()
{
  std::ofstream fout;

  //irisデータの読み込み
  cv::Ptr<cv::ml::TrainData> raw_data = cv::ml::TrainData::loadFromCSV("iris.data", 0);

  cv::Mat data(150, 4, CV_32FC1);
  //特徴量データの切り出し
  data = raw_data->getSamples();

  cv::Mat label(150, 1, CV_32SC1);
  //ラベルデータの切り出し
  label = raw_data->getResponses();

  //クラスタリング結果を保存する配列の定義
  cv::Mat centers, labels;

  //K-means法の実行（k=3の場合）
  cv::kmeans(data, 3, labels, cv::TermCriteria(cv::TermCriteria::COUNT, 100, 1.0), 0, cv::KMEANS_PP_CENTERS, centers);

  std::cout << "kmeans::labels::" << std::endl;

  for (int i = 0; i < data.rows; i++) {
    std::cout << labels.at<int>(i) << " ";
  }
  std::cout << std::endl;

  std::cout << "kmeans::centers::" << std::endl;
  for (int i = 0; i < 3; i++) {
    for (int d = 0; d < 4; d++) {
      std::cout << centers.at < float >(i, d) << " ";
    }
    std::cout << std::endl;
  }

  // 出力結果のファイルへの保存
  fout.open("data.txt");
  if (!fout.is_open()) {
    std::cerr << "ERR: fout open" << std::endl;
    return -1;
  }

  for (int i = 0; i < 150; i++) {
    fout << (int)labels.at<int>(i) << " " << (float)data.at<float>(i, 0) << " " << data.at<float>(i, 1) << " " << data.at<float>(i, 2) << std::endl;
  }
  fout.close();

  system("PAUSE");
  return 0;
}
