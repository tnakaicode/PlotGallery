#define _CRT_SECURE_NO_WARNINGS
#define _USE_MATH_DEFINES
#include <iostream>
#include <fstream>
#include <cmath>
#include <ctime>
#include <opencv2/opencv.hpp>

int main()
{
  // 特異値分解の結果を保存する行列  
  cv::Mat1d U, S, V;
  // 特異値分解の対象となる2x3の行列
  cv::Mat1d A = (cv::Mat_<double>(2, 3) << 1, 2, 3, 4, 5, 6);

  std::cout << "A=" << A << std::endl << std::endl;
  std::cout << "A rows =" << A.rows << std::endl << std::endl;
  std::cout << "A cols =" << A.cols << std::endl << std::endl;

  // 特異値分解
  cv::SVD::compute(A, S, U, V, cv::SVD::FULL_UV);

  std::cout << "U=" << U << std::endl << std::endl;
  std::cout << "S=" << S << std::endl << std::endl;
  std::cout << "V=" << V << std::endl << std::endl;

  cv::Mat1d Sinv = cv::Mat::zeros(A.cols, A.rows, CV_32F);

  std::cout << "Sinv rows =" << Sinv.rows << std::endl << std::endl;
  std::cout << "Sinv cols =" << Sinv.cols << std::endl << std::endl;

  //S行列の逆行列の計算
  Sinv(0, 0) = 1.0 / S(0);
  Sinv(1, 1) = 1.0 / S(1);

  std::cout << "S-inv =" << Sinv << std::endl << std::endl;

  // 疑似逆行列の計算
  cv::Mat1d Ainv;
  Ainv = V.t()*Sinv*U.t();

  std::cout << "V-T S-inv U-T=" << Ainv << std::endl << std::endl;

  // 検算
  std::cout << "A A-inv A =" << A*Ainv*A << std::endl << std::endl;

  system("PAUSE");
  return 0;
}
