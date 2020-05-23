#define _CRT_SECURE_NO_WARNINGS
#define _USE_MATH_DEFINES
#include <iostream>
#include <fstream>
#include <cmath>
#include <ctime>
#include <opencv2/opencv.hpp>
//
//注意：プログラムリスト18.1を含む
//
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

  cv::Mat classlabel = raw_data->getClassLabels();
  std::cout << classlabel.rows << std::endl;

  //ベクトル化した出力ラベルの配列の初期化
  std::cout << "Vector label transform \n";
  cv::Mat vector_label = cv::Mat::zeros(label.rows, classlabel.rows, CV_32FC1);

  //ラベル値のベクトル化
  for (int i = 0; i < label.rows; i++) {
    int idx = (int)label.at<float>(i, 0) - 1;
    std::cout << "label_idx:: " << idx << std::endl;

    vector_label.at<float>(i, idx) = 1.f;
  }

  //訓練データの生成
  cv::Ptr<cv::ml::TrainData>tdata = cv::ml::TrainData::create(data, cv::ml::ROW_SAMPLE, vector_label);

  //
  //ニューラルネットワークの構築
  //
  //ユニット数を設定するための配列の用意
  cv::Mat layer_sizes(3, 1, CV_32S);

  //各層におけるユニット数の設定
  layer_sizes.row(0) = 4;
  layer_sizes.row(1) = 5;
  layer_sizes.row(2) = 3; // the number of labels

  //ニューラルネットワークモデルの生成
  cv::Ptr<cv::ml::ANN_MLP> ann = cv::ml::ANN_MLP::create();
  //ネットワーク構造の設定
  ann->setLayerSizes(layer_sizes);

  //訓練方法の各種設定
  ann->setActivationFunction(cv::ml::ANN_MLP::SIGMOID_SYM, 0, 0);
  ann->setTermCriteria(cv::TermCriteria(cv::TermCriteria::MAX_ITER + cv::TermCriteria::EPS, 10000, FLT_EPSILON));
  ann->setTrainMethod(cv::ml::ANN_MLP::BACKPROP, 0.001);
  ann->setBackpropMomentumScale(0.05);
  ann->setBackpropWeightScale(0.05);

  //ニューラルネットワークの訓練
  ann->train(tdata);

  //検証データの生成
  cv::Mat testSample(1, 4, CV_32FC1);

  //検証データの例
  // 5.8, 4.0, 1.2, 0.2, label = 0
  // 5.9, 3.0, 4.2, 1.5, label = 1
  // 7.7, 3.8, 6.7, 2.2, label = 2

  testSample.at<float>(0) = 7.0;
  testSample.at<float>(1) = 3.6;
  testSample.at<float>(2) = 6.3;
  testSample.at<float>(3) = 1.95;

  //訓練されたニューラルネットワークによる予測
  std::cout << "Predicting...\n";
  cv::Mat response(1, 3, CV_32FC1);
  ann->predict(testSample, response);

  std::cout << "MLP vector response--->\n";
  std::cout << response << std::endl;

  system("PAUSE");
  return 0;
}
