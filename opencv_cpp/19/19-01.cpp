#define _CRT_SECURE_NO_WARNINGS
#define _USE_MATH_DEFINES
#include <iostream>
#include <fstream>
#include <cmath>
#include <ctime>
#include <opencv2/opencv.hpp>


int main()
{
  //irisデータの読み込み
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

  //AdaBoost識別器の構築
  cv::Ptr<cv::ml::Boost> boost = cv::ml::Boost::create();

  //AdaBoostのパラメータの設定
  boost->setBoostType(cv::ml::Boost::DISCRETE);
  boost->setWeakCount(100);
  boost->setWeightTrimRate(0.95);
  boost->setMaxDepth(2);
  boost->setUseSurrogates(false);
  boost->setPriors(cv::Mat());

  //AdaBoost識別器の訓練
  boost->train(raw_data);

  //検証データの生成
  cv::Mat testSample(1, 4, CV_32FC1);

  testSample.at<float>(0) = 5.0;
  testSample.at<float>(1) = 3.6;
  testSample.at<float>(2) = 1.3;
  testSample.at<float>(3) = 0.25;

  //訓練されたAdaBoost識別器で検証データのラベル値を予測・表示
  int response = (int)boost->predict(testSample);
  std::cout << "Adaboost response---> " << response << std::endl;

  system("PAUSE");
  return 0;
}
