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

  //k最近傍識別器の構築
  cv::Ptr<cv::ml::KNearest> knn = cv::ml::KNearest::create();

  //k最近傍識別器のパラメータの設定
  knn->setAlgorithmType(cv::ml::KNearest::Types::BRUTE_FORCE);
  knn->setDefaultK(3);
  knn->setEmax(0);
  knn->setIsClassifier(true);

  //k最近傍識別器の訓練の実行
  knn->train(data, cv::ml::SampleTypes::ROW_SAMPLE, label);

  //検証データの設定
  cv::Mat testSample(1, 4, CV_32FC1);
  testSample.at<float>(0) = 5.0;
  testSample.at<float>(1) = 3.6;
  testSample.at<float>(2) = 1.3;
  testSample.at<float>(3) = 0.25;

  //訓練されたk最近傍識別器で検証データのラベル値を予測・表示
  int response = (int)knn->predict(testSample);
  std::cout << "knn::response1---> " << response << std::endl;

  //訓練されたk最近傍識別器のモデルの保存
  knn->save("knn.xml");

  //訓練されたk最近傍識別器のモデルの読み込み
  knn = cv::Algorithm::load<cv::ml::KNearest>("knn.xml");

  //検証データの設定
  testSample.at<float>(0) = 5.8;
  testSample.at<float>(1) = 2.6;
  testSample.at<float>(2) = 4.3;
  testSample.at<float>(3) = 0.9;

  //訓練されたk最近傍識別器で検証データのラベル値を予測・表示
  response = (int)knn->predict(testSample);
  std::cout << "knn::response2---> " << response << std::endl;

  system("PAUSE");
  return 0;
}
