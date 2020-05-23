#define _CRT_SECURE_NO_WARNINGS
#include <iostream>
#include <opencv2/opencv.hpp>

#define MKSZE 5
#define MKWGT 2


cv::Mat calcProjectionMatrix(std::vector<cv::Point3f> op, std::vector<cv::Point2f> ip)
{
	cv::Mat B((int)ip.size()*2, 11, CV_64FC1);
	cv::Mat C((int)ip.size()*2,  1, CV_64FC1);
	
	for (int i = 0, j = 0; i < op.size()*2; i+=2, j++) {
		B.at<double>( i,  0 ) = op[j].x;
		B.at<double>( i,  1 ) = op[j].y;
		B.at<double>( i,  2 ) = op[j].z;
		B.at<double>( i,  3 ) = 1.0;
		
		B.at<double>( i,  4 ) = 0.0;
		B.at<double>( i,  5 ) = 0.0;
		B.at<double>( i,  6 ) = 0.0;
		B.at<double>( i,  7 ) = 0.0;
		
		B.at<double>( i,  8 ) = -ip[j].x*op[j].x;
		B.at<double>( i,  9 ) = -ip[j].x*op[j].y;
		B.at<double>( i, 10 ) = -ip[j].x*op[j].z;
		
		C.at<double>( i,  0 ) = ip[j].x;
		
		B.at<double>( i+1,  0 ) = 0.0;
		B.at<double>( i+1,  1 ) = 0.0;
		B.at<double>( i+1,  2 ) = 0.0;
		B.at<double>( i+1,  3 ) = 0.0;
		
		B.at<double>( i+1,  4 ) = op[j].x;
		B.at<double>( i+1,  5 ) = op[j].y;
		B.at<double>( i+1,  6 ) = op[j].z;
		B.at<double>( i+1,  7 ) = 1.0;
		
		B.at<double>( i+1,  8 ) = -ip[j].y*op[j].x;
		B.at<double>( i+1,  9 ) = -ip[j].y*op[j].y;
		B.at<double>( i+1, 10 ) = -ip[j].y*op[j].z;
		
		C.at<double>( i+1,  0 ) = ip[j].y;
	}
	
	// 方程式を解く
	cv::Mat pp;
	cv::solve( B, C, pp, cv::DECOMP_SVD );
	
	cv::Mat P(3, 4, CV_64FC1);
	for ( int i = 0; i < 11; i++ )  P.at<double>(i/4, i%4) = pp.at<double>( i, 0 );
	P.at<double>(2,3)=1.0;
	
	// 透視投影変換行列を分解して内部パラメータ，外部パラメータを求める
	cv::Mat A, R, t;
	cv::decomposeProjectionMatrix( P, A, R, t );
	
	return P;
}



int main( int argc, char** argv )
{
	
	const std::string  win_src = "Source";
	
	cv::Mat  img;
	cv::Mat  P;
	
	int  ix, iy, wx, wy, wz;
	
	// 座標に関する変数
	std::vector<cv::Point3f>  op;
	std::vector<cv::Point2f>  ip;
	
	// ウィンドウ名やファイル名に関するパラメータ
	const std::string  fileName = "/data_file/calibbox.jpg";
	
	//　ウィンドウ上に画像を表示
	cv::namedWindow(win_src);
	
	img = cv::imread( fileName );
	cv::imshow( win_src, img );
	
	
	//画像上の点に対応する３次元位置を入力する（最低６組の対応が必要）
	ip.push_back(cv::Point2f(467, 206));
	op.push_back(cv::Point3f(  0,   0, 150));
	
	ip.push_back(cv::Point2f(717, 250));
	op.push_back(cv::Point3f(  0, 150, 150));
	
	ip.push_back(cv::Point2f(469, 383));
	op.push_back(cv::Point3f(150, 150, 150));
	
	ip.push_back(cv::Point2f(217, 294));
	op.push_back(cv::Point3f(150,   0, 150));
	
	ip.push_back(cv::Point2f(712, 543));
	op.push_back(cv::Point3f(  0, 150,   0));
	
	ip.push_back(cv::Point2f(507, 734));
	op.push_back(cv::Point3f(150, 150,   0));
	
	ip.push_back(cv::Point2f(282, 582));
	op.push_back(cv::Point3f(150,   0,   0));
	
	
	//対応点を入力した２次元位置にxを表示
	for (int i = 0; i < ip.size(); i++) {
		ix = ip[i].x;
		iy = ip[i].y;
		cv::line(img, cv::Point(ix-MKSZE, iy-MKSZE), cv::Point(ix+MKSZE, iy+MKSZE), cv::Scalar(0, 0, 255), MKWGT);
		cv::line(img, cv::Point(ix-MKSZE, iy+MKSZE), cv::Point(ix+MKSZE, iy-MKSZE), cv::Scalar(0, 0, 255), MKWGT);
	}
	cv::imshow( win_src, img );
	
	
	//入力された行列を用いて，P行列を計算する
	P = calcProjectionMatrix(op, ip);
	
	
	//確認のために３次元位置を再投影する，再投影位置には○が表示される
	wx = 150;
	wy = 150;
	wz = 120;
	cv::Mat wpos(4, 1, CV_64FC1);
	wpos.at<double>(0,0) = wx;
	wpos.at<double>(1,0) = wy;
	wpos.at<double>(2,0) = wz;
	wpos.at<double>(3,0) = 1.0;
	
	cv::Mat ipos(3, 1, CV_64FC1);
	ipos = P * wpos;
	
	ix = ipos.at<double>(0,0) / ipos.at<double>(2,0);
	iy = ipos.at<double>(1,0) / ipos.at<double>(2,0);
	cv::circle(img, cv::Point(ix, iy), MKSZE, cv::Scalar(255, 0, 255), MKWGT);
	cv::imshow( win_src, img );
	cv::waitKey(0);
	
	return 0;
}
