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

  // irisデータの読み込み
  cv::Ptr<cv::ml::TrainData> raw_data = cv::ml::TrainData::loadFromCSV("iris.data", 0);

  // 特徴量データの切り出し
  cv::Mat data(150, 4, CV_32FC1);
  data = raw_data->getSamples();

  // ラベルデータの切り出し  
  cv::Mat label(150, 1, CV_32SC1);
  label = raw_data->getResponses();

  // PCAの実行
  cv::PCA pca(data, cv::Mat(), cv::PCA::DATA_AS_ROW, 2);
  cv::Mat result;

  // 固有値の表示
  std::cout << "eigen values" << std::endl;
  for (int n = 0; n < 2; n++) {
    std::cout << n << ", " << ((float *)pca.eigenvalues.data)[n] << std::endl;
  }

  // 固有ベクトルの表示
  std::cout << "eigen vector" << std::endl;
  for (int n = 0; n < 2; n++) {
    std::cout << ((float *)pca.eigenvectors.data)[2 * n] << " " << ((float *)pca.eigenvectors.data)[2 * n + 1] << std::endl;
  }

  // 次元圧縮されたデータの取得
  pca.project(data, result);

  // 出力結果のファイルへの保存
  fout.open("data.txt");
  if (!fout.is_open()) {
    std::cerr << "ERR: fout open" << std::endl;
    return -1;
  }

  for (int i = 0; i < 150; i++) {
    fout << (int)((float *)label.data)[i] << " " << ((float *)result.data)[2 * i] << " " << ((float *)result.data)[2 * i + 1] << std::endl;
  }
  fout.close();

  system("PAUSE");
  return 0;
}
