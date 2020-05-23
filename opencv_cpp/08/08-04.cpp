#define _CRT_SECURE_NO_WARNINGS
#include <iostream>
#include <string>
#include <vector>
#include <opencv2/opencv.hpp>

int best = 30;

int main()
{
	const std::string  file_cam_param = "/data_file/cam_param.xml";
	
	cv::Mat img_src[2], img_srcw[2], img_match, img_per, img_reg;
	std::string filename[2] = { "/data_file/regist5-1.jpg", "/data_file/regist5-2.jpg" };
	cv::Scalar color[2] = { cv::Scalar(0, 0, 255), cv::Scalar(255, 0, 0) };
	
	for (int i = 0; i < 2; i++){
		img_src[i] = cv::imread(filename[i], 1); // 画像読み込み
		cv::rectangle(img_src[i], cv::Point(0, 0), cv::Point(img_src[i].cols, img_src[i].rows), color[i], 2); // 外枠
		img_srcw[i] = cv::Mat::zeros(img_src[i].size() * 2, img_src[i].type());
		cv::Mat roi = img_srcw[i](cv::Rect(img_srcw[i].cols / 4, img_srcw[i].rows / 4, img_src[i].cols, img_src[i].rows));
		img_src[i].copyTo(roi); // 縦横倍のMatの中央にコピー
	}
	cv::imshow("img_src[0]", img_srcw[0]);
	cv::imshow("img_src[1]", img_srcw[1]);
	
	cv::waitKey(0);
	
	// (1) 特徴点抽出
	cv::Ptr<cv::AKAZE> detector = cv::AKAZE::create();
	std::vector<cv::KeyPoint> kpts1, kpts2;
	cv::Mat desc1, desc2;
	detector->detectAndCompute(img_srcw[0], cv::noArray(), kpts1, desc1);
	detector->detectAndCompute(img_srcw[1], cv::noArray(), kpts2, desc2);
	
	// 特徴点が少なすぎる場合は停止する
	std::cout << kpts1.size() << " " << kpts2.size() << std::endl;
	if(kpts1.size() < best || kpts2.size() < best) {
		std::cout << "few keypoints : "
				<< kpts1.size() << " or " << kpts2.size() << "< " << best << std::endl;
		return -1;
	}
	
	// (2) 得られた特徴点間のマッチング
	cv::BFMatcher matcher(cv::NORM_HAMMING);
	std::vector<cv::DMatch> matches;
	matcher.match(desc1, desc2, matches);
	
	std::cout << "best = " << best << std::endl;
	std::cout << "match size = " << matches.size() << std::endl;
	if (matches.size() < best) {
		std::cout << "few matchpoints" << std::endl;
	}
	
	// 上位best個を採用
	std::nth_element(begin(matches), begin(matches) + best - 1, end(matches));
	matches.erase(begin(matches) + best, end(matches));
	std::cout << "matchs size = " << matches.size() << std::endl;
	
	// 特徴点の対応を表示
	cv::drawMatches(img_srcw[0], kpts1, img_srcw[1], kpts2, matches, img_match);
	cv::imshow("matchs", img_match);
	
	// 特徴点をvectorにまとめる
	std::vector<cv::Point2f> points_src, points_dst;
	for (int i = 0; i < matches.size(); i++) {
		points_src.push_back(kpts1[matches[i].queryIdx].pt);
		points_dst.push_back(kpts2[matches[i].trainIdx].pt);
	}
	
	// (3) マッチング結果から，F行列を推定する
	cv::Mat F = cv::findFundamentalMat(points_src, points_dst);
	std::cout << "F=" << F << std::endl;
	
	// (4) カメラの内部パラメータが既知の場合はE行列を計算し，外部パラメータを推定する
	// カメラ内部パラメータ読み込み
	cv::Mat A;
	cv::FileStorage fs(file_cam_param, cv::FileStorage::READ);
	fs["intrinsic"] >> A;
	fs.release();
	std::cout << "A=" << A << std::endl;
	
	// E行列の計算
	cv::Mat E = cv::findEssentialMat(points_src, points_dst, A);
	
	// 外部パラメータ（回転，並進ベクトル）の計算
	cv::Mat R, t;
	cv::recoverPose(E, points_src, points_dst, A, R, t);
	
	cv::waitKey(0);
	
	return 0;
}
