#define _CRT_SECURE_NO_WARNINGS
#define _USE_MATH_DEFINES
#include <iostream>
#include <string>
#include <vector>
#include <cmath>
#include <ctime>
#include <iterator>
#include <opencv2/opencv.hpp>
std::string win = "main";

class Particle {
public:
  cv::Point2d pos; // 位置
  cv::Point2d vel; // 速度
  double like; // 尤度
  double wgt; // 重み
  bool keep; // 残存フラグ
  Particle(cv::Point2d pos, cv::Point2d vel, double l, double w, bool k);

  // sort用
  bool operator<(const Particle& right) const {
    return like < right.like;
  }
};

Particle::Particle(cv::Point2d p, cv::Point2d v, double l, double w, bool k)
{
  pos = p;
  vel = v;
  like = l;
  wgt = w;
  keep = k;
}

int main()
{
  cv::Mat img_src, img_hsv;
  std::vector<cv::Mat> vec_hsv(3);
  cv::VideoCapture cap("04-06.wmv");

  std::vector<Particle> P;
  cv::RNG rng((unsigned int)time(NULL));

  int num = 1000; // パーティクル数

  cap >> img_src; // 画像取得

  cv::namedWindow(win);

  // パーティクル初期化，画面全体に一様分布，初期尤度1.0，初期重み0.0
  for (int i = 0; i < num; i++) {
    cv::Point2d pt(rng.uniform(0, img_src.cols), rng.uniform(0, img_src.rows));
    Particle p(pt, cv::Point2d(0.0, 0.0), 1.0, 0.0, false);
    P.push_back(p);
  }

  cv::Point2d center(img_src.cols / 2, img_src.rows / 2);
  while (1) {
    // 予測
    for (int i = 0; i < P.size(); i++) {
      P.at(i).pos += P.at(i).vel;
    }

    cap >> img_src; // 画像取得
    cv::cvtColor(img_src, img_hsv, cv::COLOR_BGR2HSV); // HSV変換, Hは0～180，S,Vは0～255
    cv::split(img_hsv, vec_hsv); // HSV分離

    // 色相値，彩度値から尤度を計算，更新
    for (int i = 0; i < P.size(); i++) {
      if (0 < P.at(i).pos.x && P.at(i).pos.x < img_src.cols
        && 0 < P.at(i).pos.y && P.at(i).pos.y < img_src.rows) {
        int h = vec_hsv[0].at<unsigned char>(P.at(i).pos); // パーティクルの画素の色相値取得
        int s = vec_hsv[1].at<unsigned char>(P.at(i).pos); // パーティクルの画素の彩度値取得
        double len_h = abs(70 - h); // H=70からの距離
        double len_s = abs(200 - s); // S=200からの距離
        double like = (len_h / 180)*0.8 + (len_s / 255)*0.2; // 尤度関数，0 <= like <= 1
        P.at(i).like = 1 - like; // 最高尤度を1とする
      }
      else {
        P.at(i).like = 0;
      }
    }

    // 尤度を昇順にソート
    sort(P.begin(), P.end());

    // 比較的高尤度パーティクルの残存と，低尤度パーティクルの削除
    double thresh_like = 0.9; // 尤度の閾値
    int thresh_keep = P.size() / 100; // 残存パーティクル数 1%
    for (int i = 0; i < P.size(); i++) {
      if (P.at(i).like > thresh_like || i > (P.size() - thresh_keep)) P.at(i).keep = true;
      else P.at(i).keep = false;
    }
    std::vector<Particle>::iterator it = P.begin();
    while (it != P.end()) {
      if ((*it).keep) it++;
      else it = P.erase(it);
    }

    // 高尤度パーティクルの計数，尤度の合計
    int count = P.size();
    double l_sum = 0.0;
    for (int i = 0; i < P.size(); i++) {
      l_sum += P.at(i).like;
    }

    // 正規化した重みを計算
    for (int i = 0; i < P.size(); i++) {
      P.at(i).wgt = P.at(i).like / l_sum;
    }

    // リサンプリング
    std::vector<Particle> Pnew;
    for (int i = 0; i < P.size(); i++) {
      int num_new = P.at(i).wgt * (num - P.size());
      for (int j = 0; j < num_new; j++) {
        double r = rng.gaussian(img_src.rows + img_src.cols) * (1 - P.at(i).like);
        double ang = rng.uniform(-M_PI, M_PI);
        cv::Point2d pt(r*cos(ang) + P.at(i).pos.x, r*sin(ang) + P.at(i).pos.y);
        Particle p(pt, pt - P.at(i).pos, P.at(i).like, P.at(i).wgt, false); // 等速直線運動と仮定
        Pnew.push_back(p);
      }
    }
    std::copy(Pnew.begin(), Pnew.end(), std::back_inserter(P));

    // パーティクル描画
    for (int i = 0; i < P.size(); i++) {
      if (0 < P.at(i).pos.x && P.at(i).pos.x < img_src.cols
        && 0 < P.at(i).pos.y && P.at(i).pos.y < img_src.rows) {
        cv::circle(img_src, P.at(i).pos, 2, cv::Scalar(0, 0, 255));
      }
    }

    // 追加パーティクルの描画
    for (int i = 0; i < Pnew.size(); i++) {
      cv::circle(img_src, Pnew.at(i).pos, 2, cv::Scalar(255, 0, 0));
    }

    // パーティクルの重心
    for (int i = 0; i < P.size(); i++) {
      center += P.at(i).pos;
    }
    center *= 1.0 / P.size();
    cv::line(img_src, cv::Point(center.x, 0), cv::Point(center.x, img_src.rows), cv::Scalar(0, 255, 255), 3);
    cv::line(img_src, cv::Point(0, center.y), cv::Point(img_src.cols, center.y), cv::Scalar(0, 255, 255), 3);

    cv::imshow(win, img_src);
    if (cv::waitKey(1) == 'q') break;
  }
  return 0;
}
