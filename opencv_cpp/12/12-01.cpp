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

  //乱数生成器を初期化
  cv::RNG rng((unsigned int)time(NULL));

  int num_data = 1000; //データの総数を表す変数
  int num_dim = 2; //1つのデータの次元数を表す変数
  int num_eig = 2; //固有ベクトルの個数を表す変数

  //計算対象となるデータが保存されている行列の定義
  cv::Mat samples(num_dim, num_data, CV_64FC1);

  //人工的データの生成（2次元の楕円状に分布する点群）
  for (int i = 0; i < num_data; i++) {
    double x = 0.6*rng.gaussian(1.0);
    double y = 0.2*rng.gaussian(1.0);
    double angle = M_PI / 4;
    samples.at<double>(0, i) = cos(angle)*x - sin(angle)*y;
    samples.at<double>(1, i) = sin(angle)*x + cos(angle)*y;
  }

  // 主成分分析を実行する
  cv::PCA pca(samples, cv::Mat(), cv::PCA::DATA_AS_COL, num_eig);

  // 固有値の表示
  std::cout << "eigen values :" << std::endl;
  for (int n = 0; n < num_eig; n++) {
    std::cout << n << " , " << pca.eigenvalues.at<double>(n) << std::endl;
  }

  // 固有ベクトルの表示
  std::cout << "eigen vector :" << std::endl;
  for (int n = 0; n < num_eig; n++) {
    for (int d = 0; d < num_dim; d++) {
      std::cout << pca.eigenvectors.at<double>(n, d);
      if (d < 1) std::cout << " , ";
      else std::cout << std::endl;
    }
  }

  //生成したデータのファイルへの保存
  fout.open("data.txt");
  if (!fout.is_open()) {
    std::cerr << "ERR: fout open" << std::endl;
    return -1;
  }

  for (int i = 0; i < num_data; i++) {
    fout << samples.at<double>(0, i) << " " << samples.at<double>(1, i) << std::endl;
  }

  fout.close();

  system("PAUSE");
  return 0;
}
