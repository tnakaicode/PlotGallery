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

  //訓練データ（irisデータ）の読み込み
  cv::Ptr<cv::ml::TrainData> raw_data = cv::ml::TrainData::loadFromCSV("iris.data", 0);

  //特徴量データの切り出し
  cv::Mat data(150, 4, CV_32FC1);
  data = raw_data->getSamples();
  std::cout << data << std::endl;
  std::cout << data.rows << " x " << data.cols << std::endl;

  //ラベルデータの切り出し
  cv::Mat label(150, 1, CV_32SC1);
  label = raw_data->getResponses();
  std::cout << label << std::endl;
  std::cout << label.rows << " x " << label.cols << std::endl;

  //ベイズ識別器の構築
  cv::Ptr<cv::ml::NormalBayesClassifier> nbc = cv::ml::NormalBayesClassifier::create();

  //ベイズ識別器の訓練
  nbc->train(raw_data);

  //検証データの設定
  cv::Mat testSample(1, 4, CV_32FC1);

  testSample.at<float>(0) = 5.0;
  testSample.at<float>(1) = 3.6;
  testSample.at<float>(2) = 1.3;
  testSample.at<float>(3) = 0.25;

  //訓練された傍識別器で検証データのラベル値を予測・表示
  int response = (int)nbc->predict(testSample);
  std::cout << "NBC response---> " << response << std::endl;

  system("PAUSE");
  return 0;

}
