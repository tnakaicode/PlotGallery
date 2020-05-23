#define _CRT_SECURE_NO_WARNINGS
#define _USE_MATH_DEFINES
#include <iostream>
#include <fstream>
#include <cmath>
#include <ctime>
#include <opencv2/opencv.hpp>

// 識別境界を与える関数
int f(float x, float y) {
  return y > 0.5*sin(x * 8) + 0.5 ? 0 : 1;
}

// 設定した関数に従ってラベル値を決定する関数
cv::Mat labelData(cv::Mat points) {
  cv::Mat labels(points.rows, 1, CV_32FC1);
  for (int i = 0; i < points.rows; i++) {
    float x = points.at<float>(i, 0);
    float y = points.at<float>(i, 1);
    labels.at<float>(i, 0) = f(x, y);
  }
  return labels;
}

int main()
{
  int numTrainingPoints = 200;
  int numTestPoints = 2000;
  std::ofstream fout;

  cv::Mat trainingData(numTrainingPoints, 2, CV_32FC1);
  cv::Mat testData(numTestPoints, 2, CV_32FC1);

  cv::randu(trainingData, 0, 1);
  cv::randu(testData, 0, 1);

  cv::Mat trainingClasses = labelData(trainingData);
  cv::Mat testClasses = labelData(testData);

  //訓練データの生成
  cv::Ptr<cv::ml::TrainData> train_data = cv::ml::TrainData::create(trainingData, cv::ml::ROW_SAMPLE, trainingClasses);
  //検証用データの生成
  cv::Ptr<cv::ml::TrainData> test_data = cv::ml::TrainData::create(testData, cv::ml::ROW_SAMPLE, testClasses);

  //混同行列の初期化
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
  knn->train(train_data);

  //訓練データに対する混同行列の計算
  for (int i = 0; i < trainingData.rows; i++) {
    //真のクラス
    int actual_response = (int)trainingClasses.at<float>(i, 0);
    std::cout << trainingData.row(i) << std::endl;

    //識別されたクラス
    int response = (int)knn->predict(trainingData.row(i));
    std::cout << "(" << i << ")" << actual_response << "-->" << response << std::endl;

    confusion_matrix.at<double>(response, actual_response)++;
  }
  std::cout << "Confusion Matrix(Train) =" << confusion_matrix << std::endl;

  //訓練データの保存
  fout.open("data-train.txt");
  if (!fout.is_open()) {
    std::cerr << "ERR: fout open" << std::endl;
    return -1;
  }

  for (int i = 0; i < trainingData.rows; i++) {
    fout << (int)trainingClasses.at<float>(i, 0) << " " << trainingData.at<float>(i, 0) << " " << trainingData.at<float>(i, 1) << std::endl;
  }
  fout.close();


  //検証用データの保存
  fout.open("data-test.txt");
  if (!fout.is_open()) {
    std::cerr << "ERR: fout open" << std::endl;
    return -1;
  }
  for (int i = 0; i < testData.rows; i++) {
    fout << (int)testClasses.at<float>(i, 0) << " " << testData.at<float>(i, 0) << " " << testData.at<float>(i, 1) << std::endl;
  }
  fout.close();


  //検証用データの混同行列の初期化
  confusion_matrix = (cv::Mat_<double>(2, 2) << 0, 0, 0, 0);

  //訓練したKNNによる検証用データの識別結果の保存
  fout.open("data-test-predict.txt");
  if (!fout.is_open()) {
    std::cerr << "ERR: fout open" << std::endl;
    return -1;
  }

  for (int i = 0; i < testData.rows; i++) {
    //真のクラス
    int actual_response = (int)testClasses.at<float>(i, 0);
    std::cout << testData.row(i) << std::endl;

    //識別されたクラス
    int response = (int)knn->predict(testData.row(i));
    std::cout << "(" << i << ")" << actual_response << "-->" << response << std::endl;
    fout << response << " " << testData.at<float>(i, 0) << " " << testData.at<float>(i, 1) << std::endl;

    confusion_matrix.at<double>(response, actual_response)++;
  }
  std::cout << "Confusion Matrix(Test) =" << confusion_matrix << std::endl;

  system("PAUSE");
  return 0;
}
