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

  //決定木の構築
  cv::Ptr<cv::ml::DTrees> dtree = cv::ml::DTrees::create();

  //決定木のパラメータの設定
  dtree->setMaxDepth(8);
  dtree->setMinSampleCount(2);
  dtree->setUseSurrogates(false);
  dtree->setCVFolds(0); // the number of cross-validation folds
  dtree->setUse1SERule(false);
  dtree->setTruncatePrunedTree(false);

  //決定木の訓練
  dtree->train(raw_data);

  //検証データを生成
  cv::Mat testSample(1, 4, CV_32FC1);

  testSample.at<float>(0) = 5.0;
  testSample.at<float>(1) = 3.6;
  testSample.at<float>(2) = 1.3;
  testSample.at<float>(3) = 0.25;

  //訓練された決定木で検証データのラベル値を予測・表示　
  int response = (int)dtree->predict(testSample);
  std::cout << "DTrees response ---> " << response << std::endl;

  system("PAUSE");
  return 0;
}
