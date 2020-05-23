#define _CRT_SECURE_NO_WARNINGS
#include <iostream>
#include <string>
#include <opencv2/opencv.hpp>

const std::string  windowDisparity = "Disparity";
const std::string  fileLeft  = "./09-04-a.png";
const std::string  fileRight = "./09-04-b.png";

int main()
{
	
	//（１）画像ファイルの読み込み
	cv::Mat imgLeft = cv::imread( fileLeft, cv::IMREAD_GRAYSCALE );
	cv::Mat imgRight = cv::imread( fileRight, cv::IMREAD_GRAYSCALE );
	if( imgLeft.empty() || imgRight.empty() ){
		std::cout<< " --指定されたファイルがありません！" << std::endl;
		return -1;
	}
	
	// 視差画像用の領域確保
	cv::Mat imgDisparity16S = cv::Mat( imgLeft.rows, imgLeft.cols, CV_16S );
	cv::Mat imgDisparity8U  = cv::Mat( imgLeft.rows, imgLeft.cols, CV_8UC1 );
	
	//（２）StereoBMクラスのインスタンスを生成
	int ndisparities = 16*5; // 探索したいdisparitiesの最大値を１６の倍数で指定
	int SADWindowSize = 21;  // ブロック窓のサイズ，最大２１の奇数で指定
	
	cv::Ptr<cv::StereoBM> sbm = cv::StereoBM::create( ndisparities, SADWindowSize );
	
	//（３）視差画像を計算
	sbm->compute( imgLeft, imgRight, imgDisparity16S );
	
	//（４）視差画像の最小値が０，最大値が２５５になるように線形変換（正規化）して表示
	double minVal, maxVal;
	cv::minMaxLoc( imgDisparity16S, &minVal, &maxVal );
	imgDisparity16S.convertTo( imgDisparity8U, CV_8UC1, 255/(maxVal - minVal));
	
	cv::namedWindow( windowDisparity, cv::WINDOW_NORMAL );
	cv::imshow( windowDisparity, imgDisparity8U );
	
	//（５）視差画像をファイルに保存
	cv::imwrite("./SBM_sample.jpg", imgDisparity16S);
	
	cv::waitKey(0);
	
	return 0;
}
