#define _CRT_SECURE_NO_WARNINGS
#define _USE_MATH_DEFINES
#include <iostream>
#include <fstream>
#include <cmath>
#include <ctime>
#include <opencv2/opencv.hpp>

int main()
{
  //訓練データの読み込み
  cv::Ptr<cv::ml::TrainData> raw_data = cv::ml::TrainData::loadFromCSV("pima-indians-diabetes.csv", 0);

  //乱数生成器を初期化．
  cv::RNG rng((unsigned int)time(NULL));

  //読込んだデータの内80%を訓練に使用するように設定
  raw_data->setTrainTestSplitRatio(0.8, true);

  //読込んだ全てのデータとそのラベル
  cv::Mat data = raw_data->getSamples();
  cv::Mat label = raw_data->getResponses();

  //訓練データとそのラベル
  cv::Mat trdata = raw_data->getTrainSamples();
  cv::Mat trlabel = raw_data->getTrainResponses();

  //検証用データのインデックスの読込
  cv::Mat data_ts_idx = raw_data->getTestSampleIdx();
  std::cout << data_ts_idx << std::endl;
  std::cout << data_ts_idx.rows << "x" << data_ts_idx.cols << std::endl;

  //混合行列を保存する配列の初期化
  cv::Mat confusion_matrix = (cv::Mat_<double>(2, 2) << 0, 0, 0, 0);
  std::cout << "Confusion Matrix =" << confusion_matrix << std::endl;


  //KNNの構築
  cv::Ptr<cv::ml::KNearest> knn = cv::ml::KNearest::create();
  //KNNの各種設定
  knn->setAlgorithmType(cv::ml::KNearest::Types::BRUTE_FORCE);
  knn->setDefaultK(3);
  knn->setEmax(0);
  knn->setIsClassifier(true);

  //KNNの訓練
  knn->train(raw_data);

  //訓練，検証用データによる誤り率の計算
  cv::Mat train_responses, test_responses;
  float fl1 = knn->calcError(raw_data, false, train_responses);
  float fl2 = knn->calcError(raw_data, true, test_responses);

  std::cout << "Error train " << fl1 << "(" << train_responses.rows << ")" << std::endl;
  std::cout << "Error test  " << fl2 << "(" << test_responses.rows << ")" << std::endl;

  std::cout << train_responses << std::endl;
  std::cout << train_responses.rows << "x" << train_responses.cols << std::endl;

  //訓練データに対する混同行列の計算
  for (int i = 0; i < train_responses.rows; i++) {
    //真のクラス
    int actual_response = (int)trlabel.at<float>(i, 0);
    std::cout << trdata(cv::Rect(0, i, 8, 1)) << std::endl;

    //識別されたクラス
    int response = (int)knn->predict(trdata(cv::Rect(0, i, 8, 1)));
    std::cout << "(" << i << ") " << actual_response << "--> " << response << std::endl;

    confusion_matrix.at<double>(response, actual_response)++;
  }

  std::cout << "Confusion Matrix(Train) =" << confusion_matrix << std::endl;
  confusion_matrix = (cv::Mat_<double>(2, 2) << 0, 0, 0, 0);

  for (int i = 0; i < test_responses.rows; i++) {
    std::cout << "(" << (int)data_ts_idx.at<int>(0, i) << ") " << std::endl;
  }

  //検証用データに対する混同行列の計算
  for (int i = 0; i < test_responses.rows; i++) {
    //真のクラス
    int actual_response = (int)label.at<float>((int)data_ts_idx.at<int>(0, i), 0);
    std::cout << data(cv::Rect(0, (int)data_ts_idx.at<int>(0, i), 8, 1)) << std::endl;

    //識別されたクラス
    int response = (int)knn->predict(data(cv::Rect(0, (int)data_ts_idx.at<int>(0, i), 8, 1)));
    std::cout << "(" << i << ") " << actual_response << "--> " << response << std::endl;

    confusion_matrix.at<double>(response, actual_response)++;
  }

  std::cout << "Confusion Matrix(Test) =" << confusion_matrix << std::endl;

  system("PAUSE");
  return 0;
}
