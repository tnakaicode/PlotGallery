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

  //SVMの構築
  cv::Ptr<cv::ml::SVM> svm = cv::ml::SVM::create();

  //SVMのパラメータの設定
  svm->setType(cv::ml::SVM::C_SVC);
  svm->setKernel(cv::ml::SVM::LINEAR); //SVM::LINEAR;
  svm->setDegree(0.5);
  svm->setGamma(1);
  svm->setCoef0(1);
  svm->setNu(0.5);
  svm->setP(0);
  svm->setTermCriteria(cv::TermCriteria(cv::TermCriteria::MAX_ITER + cv::TermCriteria::EPS, 1000, 0.01));
  svm->setC(1.0);

  //SVMの訓練
  //svm->train(data, cv::ml::ROW_SAMPLE, label);
  svm->train(raw_data);


  //検証データの設定
  cv::Mat testSample(1, 4, CV_32FC1);
  testSample.at<float>(0) = 5.0;
  testSample.at<float>(1) = 3.6;
  testSample.at<float>(2) = 1.3;
  testSample.at<float>(3) = 0.25;

  //訓練されたSVMによる識別器で検証データのラベル値を予測・表示
  int response = (int)svm->predict(testSample);
  std::cout << "svm::response---> " << response << std::endl;


  //サポートベクトルの取得
  cv::Mat sv = svm->getSupportVectors();

  for (int i = 0; i < sv.rows; i++) {
    const float* supportVector = sv.ptr<float>(i);

    std::cout << "(" << supportVector[0] << " " << supportVector[1] << ")" << std::endl;
  }

  system("PAUSE");
  return 0;

}
