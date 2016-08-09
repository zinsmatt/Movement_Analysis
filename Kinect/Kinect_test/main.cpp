#include <iostream>
#include <Windows.h>
#include <NuiApi.h>
#include <SFML/Graphics.hpp>
#include <fstream>
#include <chrono>
#include <fstream>
#include "connexion.h"

#define POS_OK 1
#define POS_UND 99

using namespace std;

const int width = 640;
const int height = 480;
int half_width = width / 2;
int half_height = height / 2;

HANDLE stream;
sf::Uint8  *pixels = new sf::Uint8[width * height * 4];
sf::Image   image;

struct Data {
	long long time;
	float x;
	float y;
};

std::vector<long long> tab;
std::vector<Data> left_hand_tab;
std::vector<Data> right_hand_tab;




sf::Vertex hand_left;
sf::Vertex hand_right;
sf::Vertex elbow_left;
sf::Vertex elbow_right;
sf::Vertex shoulder_left;
sf::Vertex shoulder_right;
sf::Vertex shoulder_center;
sf::Vertex head;
sf::Vertex hip_left;
sf::Vertex hip_right;
sf::Vertex knee_left;
sf::Vertex knee_right;
sf::Vertex hip_center;


char *isTrackingPtr = NULL;
char *isRecordingPtr = NULL;
char *dataPtr = NULL;
bool was_recording = false;
void initDepthStream()
{
	NuiInitialize(/*NUI_INITIALIZE_FLAG_USES_DEPTH |*/ NUI_INITIALIZE_FLAG_USES_SKELETON);
	/*if (NuiImageStreamOpen(NUI_IMAGE_TYPE_DEPTH, NUI_IMAGE_RESOLUTION_640x480, 0, 2, NULL, &stream) != S_OK)
	{
		cout << "Error open stream\n";
		exit(-1);
	}*/
}


void writeDataToFile()
{
	char buffer[1024];

	ofstream file_left;
	file_left.open("data_hand_left.txt");
	for (int i = 0; i < left_hand_tab.size(); i++)
	{
		sprintf(buffer, "%lld %lf %lf\n", left_hand_tab[i].time, left_hand_tab[i].x, left_hand_tab[i].y);
		file_left << buffer;
	}
	file_left.close();

	ofstream file_right;
	file_right.open("data_hand_right.txt");
	for (int i = 0; i < right_hand_tab.size(); i++)
	{
		sprintf(buffer, "%lld %lf %lf\n", right_hand_tab[i].time, right_hand_tab[i].x, right_hand_tab[i].y);
		file_right << buffer;
	}
	file_right.close();

	right_hand_tab.clear();
	left_hand_tab.clear();

}

void drawStream()
{
	const NUI_IMAGE_FRAME* frame = NULL;
	NUI_LOCKED_RECT lockedRect;
	
	if (NuiImageStreamGetNextFrame(stream, 0, &frame) != S_OK)
	{
		cout << "Error get next frame\n";
		return;
	}
	else
	{
		std::cout << "frame OK\n";
		INuiFrameTexture* texture = frame->pFrameTexture;

		texture->LockRect(0, &lockedRect, NULL, 0);

		if (lockedRect.Pitch != 0)
		{
			int i = 0,j=0;
			const USHORT* curr = (const USHORT*)lockedRect.pBits;
			const USHORT* end = curr + (width * height);
			while (curr != end)
			{
				USHORT depth = NuiDepthPixelToDepth(*curr++);
				USHORT value = depth % 256;
		
				sf::Color coul(value, value, value, 255);

				image.setPixel(j,i, coul);
				j++;
				if (j == width) {
					j = 0;
					i++;
				}
			}
		}

		texture->UnlockRect(0);
		NuiImageStreamReleaseFrame(stream, frame);
	}
}

void adjust_coordinates()
{
	hand_left.color = sf::Color::Red;
	hand_right.color = sf::Color::Red;
	//elbow_left.color = sf::Color::Red;
	//elbow_right.color = sf::Color::Red;
	//shoulder_left.color = sf::Color::Red;
	//shoulder_right.color = sf::Color::Red;
	//shoulder_center.color = sf::Color::Red;
	//head.color = sf::Color::Red;
	//hip_left.color = sf::Color::Red;
	//hip_right.color = sf::Color::Red;
	//knee_left.color = sf::Color::Red;
	//knee_right.color = sf::Color::Red;
	//hip_center.color = sf::Color::Red;


	hand_right.position.x = (hand_right.position.x + 1)*half_width;
	hand_left.position.x = (hand_left.position.x + 1)*half_width;
	//elbow_right.position.x = (elbow_right.position.x + 1)*half_width;
	//elbow_left.position.x = (elbow_left.position.x + 1)*half_width;
	//shoulder_right.position.x = (shoulder_right.position.x + 1)*half_width;
	//shoulder_left.position.x = (shoulder_left.position.x + 1)*half_width;
	//shoulder_center.position.x = (shoulder_center.position.x + 1)*half_width;
	//head.position.x = (head.position.x + 1)*half_width;
	//hip_right.position.x = (hip_right.position.x + 1)*half_width;
	//hip_left.position.x = (hip_left.position.x + 1)*half_width;
	//knee_right.position.x = (knee_right.position.x + 1)*half_width;
	//knee_left.position.x = (knee_left.position.x + 1)*half_width;
	//hip_center.position.x = (hip_center.position.x + 1)*half_width;

	hand_right.position.y = (1-hand_right.position.y )*half_height;
	hand_left.position.y = (1-hand_left.position.y )*half_height;
	//elbow_right.position.y = (1 - elbow_right.position.y)*half_height;
	//elbow_left.position.y = (1 - elbow_left.position.y)*half_height;
	//shoulder_right.position.y = (1-shoulder_right.position.y )*half_height;
	//shoulder_left.position.y = (1 - shoulder_left.position.y)*half_height;
	//shoulder_center.position.y = (1 - shoulder_center.position.y)*half_height;
	//head.position.y = (1- head.position.y)*half_height;
	//hip_right.position.y = (1 - hip_right.position.y)*half_height;
	//hip_left.position.y = (1 - hip_left.position.y)*half_height;
	//knee_right.position.y = (1 - knee_right.position.y)*half_height;
	//knee_left.position.y = (1 - knee_left.position.y)*half_height;
	//hip_center.position.y = (1 - hip_center.position.y)*half_height;

}

int track_skeleton()
{
	NUI_SKELETON_FRAME ourframe;
	HRESULT res = NuiSkeletonGetNextFrame(0, &ourframe);
	using namespace std::chrono;
	long long ms = duration_cast<std::chrono::milliseconds>(system_clock::now().time_since_epoch()).count();
	//std::cout << "ms = " << ms << std::endl;
	if (res == S_OK)
	{
		int i = 0;
		for (int i = 0; i < 6; i++)
		{
			//std::cout << i << " ";
			if (ourframe.SkeletonData[i].eTrackingState == NUI_SKELETON_TRACKED)
			{
				//std::cout << "OK\n";
				//tab.push_back(ms);


				hand_right.position.x = ourframe.SkeletonData[i].SkeletonPositions[NUI_SKELETON_POSITION_HAND_RIGHT].x;
				hand_right.position.y = ourframe.SkeletonData[i].SkeletonPositions[NUI_SKELETON_POSITION_HAND_RIGHT].y;

				hand_left.position.x = ourframe.SkeletonData[i].SkeletonPositions[NUI_SKELETON_POSITION_HAND_LEFT].x;
				hand_left.position.y = ourframe.SkeletonData[i].SkeletonPositions[NUI_SKELETON_POSITION_HAND_LEFT].y;

				//elbow_right.position.x = ourframe.SkeletonData[i].SkeletonPositions[NUI_SKELETON_POSITION_ELBOW_RIGHT].x;
				//elbow_right.position.y = ourframe.SkeletonData[i].SkeletonPositions[NUI_SKELETON_POSITION_ELBOW_RIGHT].y;

				//elbow_left.position.x = ourframe.SkeletonData[i].SkeletonPositions[NUI_SKELETON_POSITION_ELBOW_LEFT].x;
				//elbow_left.position.y = ourframe.SkeletonData[i].SkeletonPositions[NUI_SKELETON_POSITION_ELBOW_LEFT].y;

				//shoulder_right.position.x = ourframe.SkeletonData[i].SkeletonPositions[NUI_SKELETON_POSITION_SHOULDER_RIGHT].x;
				//shoulder_right.position.y = ourframe.SkeletonData[i].SkeletonPositions[NUI_SKELETON_POSITION_SHOULDER_RIGHT].y;

				//shoulder_left.position.x = ourframe.SkeletonData[i].SkeletonPositions[NUI_SKELETON_POSITION_SHOULDER_LEFT].x;
				//shoulder_left.position.y = ourframe.SkeletonData[i].SkeletonPositions[NUI_SKELETON_POSITION_SHOULDER_LEFT].y;

				//shoulder_center.position.x = ourframe.SkeletonData[i].SkeletonPositions[NUI_SKELETON_POSITION_SHOULDER_CENTER].x;
				//shoulder_center.position.y = ourframe.SkeletonData[i].SkeletonPositions[NUI_SKELETON_POSITION_SHOULDER_CENTER].y;

				//head.position.x = ourframe.SkeletonData[i].SkeletonPositions[NUI_SKELETON_POSITION_HEAD].x;
				//head.position.y = ourframe.SkeletonData[i].SkeletonPositions[NUI_SKELETON_POSITION_HEAD].y;

				//hip_right.position.x = ourframe.SkeletonData[i].SkeletonPositions[NUI_SKELETON_POSITION_HIP_RIGHT].x;
				//hip_right.position.y = ourframe.SkeletonData[i].SkeletonPositions[NUI_SKELETON_POSITION_HIP_LEFT].y;

				//hip_left.position.x = ourframe.SkeletonData[i].SkeletonPositions[NUI_SKELETON_POSITION_HIP_LEFT].x;
				//hip_left.position.y = ourframe.SkeletonData[i].SkeletonPositions[NUI_SKELETON_POSITION_HIP_LEFT].y;

				//hip_center.position.x = ourframe.SkeletonData[i].SkeletonPositions[NUI_SKELETON_POSITION_HIP_CENTER].x;
				//hip_center.position.y = ourframe.SkeletonData[i].SkeletonPositions[NUI_SKELETON_POSITION_HIP_CENTER].y;

				//knee_right.position.x = ourframe.SkeletonData[i].SkeletonPositions[NUI_SKELETON_POSITION_KNEE_RIGHT].x;
				//knee_right.position.y = ourframe.SkeletonData[i].SkeletonPositions[NUI_SKELETON_POSITION_KNEE_RIGHT].y;

				//knee_left.position.x = ourframe.SkeletonData[i].SkeletonPositions[NUI_SKELETON_POSITION_KNEE_LEFT].x;
				//knee_left.position.y = ourframe.SkeletonData[i].SkeletonPositions[NUI_SKELETON_POSITION_KNEE_LEFT].y;

				adjust_coordinates();

				if (*isRecordingPtr == 1)
				{
					//std::cout << "Recording on\n";
					Data d;
					d.time = ms;
					d.x = hand_left.position.x;
					d.y = hand_left.position.y;
					left_hand_tab.push_back(d);
					d.x = hand_right.position.x;
					d.y = hand_right.position.y;
					right_hand_tab.push_back(d);
					was_recording = true;
					//system("cls");
				}

				if (was_recording == true && *isRecordingPtr == 0)
				{
					was_recording = false;
					writeDataToFile();
				}
				return 1;
			}
			//std::cout << "NNOK\n";

				
		}
		return 2;
	}
	//else
	//	std::cout << " erreur tracking skeleton" << std::endl;
	return 0;
}



void drawPoint(const sf::Vertex& pos,  sf::RenderWindow& window, float size)
{
	//circle1.setPosition(pos.position.x, pos.position.y);
	//circle2.setPosition(pos.position.x, pos.position.y);
	//window.draw(circle);
}

using namespace std::chrono;
int main(int argc, char **argv)
{
	//test();
	cout << "debut\n";

	std::cout << "open mmap\n";
	SharedMemory shm = { 0 };
	shm.Size = 8192;
	sprintf(shm.MapName, "Local\\Test");
	char* ptr = NULL;


	if (CreateMemoryMap(&shm))
	{
		ptr = (char*)shm.pData;
		memset(ptr, 0, shm.Size);

		while (ptr && (*ptr == 0))
		{
			//Sleep(100);
			// wait python
		}
		*ptr = 0;
		ptr++;
		// msg recu
		std::cout << "msg recu = " << std::endl;
		Sleep(0.3);
		*ptr = 1;
		std::cout << "wrote 1" << std::endl;

		isTrackingPtr = (char*)shm.pData;
		isRecordingPtr = isTrackingPtr + 1;
		dataPtr = isRecordingPtr + 1;
	}
	else {
		std::cout << "Probleme : creation du fichier partagé\n";
		exit(0);
	}


	//connexion();

	

	
	initDepthStream();

	//image.create(width, height, pixels);

	sf::RenderWindow window(sf::VideoMode(width,height), "SFML works!");
	sf::Texture  texture;
	texture.create(width, height);	
	sf::Sprite sprite;

	sf::CircleShape circle1(5);
	circle1.setFillColor(sf::Color(255, 255, 0, 255));

	sf::CircleShape circle2(5);
	circle2.setFillColor(sf::Color(255, 255, 0, 255));

	long long ta=0, tb=0;
	int it = 0;
	int ret;
	while (window.isOpen())
	{
		
		//auto t1 = std::chrono::system_clock::now();
		//long long t1 = duration_cast<std::chrono::milliseconds>(system_clock::now().time_since_epoch()).count();


		sf::Event event;
		while (window.pollEvent(event))
		{
			if (event.type == sf::Event::Closed)
				window.close();
		}

		window.clear();
		//drawStream();
		/*tb = duration_cast<std::chrono::milliseconds>(system_clock::now().time_since_epoch()).count();
		if (it > 0)
		{
			long long d = tb - ta;
			//tab.push_back(d);
			Sleep(10-d);
		
		}*/
		ret = track_skeleton();
		if (ret == 0) continue;
		//std::cout << "Tracking =  " << ret << std::endl;
		if (*isTrackingPtr == 0 && ret == 1) {
			*isTrackingPtr = 1;
			std::cout << "tracking = " << *isTrackingPtr << std::endl;
		}
		else if (*isTrackingPtr == 1 && ret == 2) {
			*isTrackingPtr = 0;
			std::cout << "tracking = " << *isTrackingPtr << std::endl;
		}

		//ta = duration_cast<std::chrono::milliseconds>(system_clock::now().time_since_epoch()).count();
		//++it;
		//texture.loadFromImage(image);
		//sprite.setTexture(texture,true);
		//window.draw(sprite);
		
		//circle.setPosition((position.x + 1)*(half_width), (1 - position.y)*(half_height));
		//file << (1 - position.x)*(half_width) << " " << (position.y - 1)*(half_height) << "\n";


		//drawPoint(head, window, 10);
		//drawPoint(hand_left, window,15);
		//drawPoint(hand_right, window,15);

		circle1.setPosition(hand_left.position.x, hand_left.position.y);
		circle2.setPosition(hand_right.position.x, hand_right.position.y);
		window.draw(circle1);
		window.draw(circle2);

		//sf::Vertex line[] = { hand_left, elbow_left, shoulder_left,shoulder_center,shoulder_right, elbow_right, hand_right };
		//window.draw(line, 7, sf::LinesStrip);
		//sf::Vertex line2[] = { shoulder_center,hip_center };
		//window.draw(line2, 2, sf::LinesStrip);
		//sf::Vertex line3[] = { knee_left,hip_left,hip_center,hip_right,knee_right };
		//window.draw(line3, 5, sf::LinesStrip);


		window.display();
		//auto t2 = std::chrono::system_clock::now();
		//long long t2 = duration_cast<std::chrono::milliseconds>(system_clock::now().time_since_epoch()).count();

		/*if (isTracking)
		{
			tab.push_back(t1);
			tab.push_back(t2);
		}*/


		//auto d = std::chrono::duration_cast<std::chrono::milliseconds>(t2 - t1);
		//std::cout << d.count() << "\n";
		//system("cls");
	
	}

	
	FreeMemoryMap(&shm);

	NuiShutdown();

	/*ofstream myfile;
	myfile.open("data.dat");
	for (int i = 0; i < tab.size(); i++)
		myfile << tab[i] << "\n";
	myfile.close();
	

	char buffer[1024];

	ofstream file_left;
	file_left.open("data_hand_left.txt");
	for (int i = 0; i < left_hand_tab.size(); i++)
	{
		sprintf(buffer, "%lld %lf %lf\n", left_hand_tab[i].time, left_hand_tab[i].x, left_hand_tab[i].y);
		file_left << buffer;
	}
	file_left.close();

	ofstream file_right;
	file_right.open("data_hand_right.txt");
	for (int i = 0; i < right_hand_tab.size(); i++)
	{
		sprintf(buffer, "%lld %lf %lf\n", right_hand_tab[i].time, right_hand_tab[i].x, right_hand_tab[i].y);
		file_right << buffer;
	}
	file_right.close();*/

	// FIN



	//cout << "Hello world" << endl;
	//NuiInitialize(NUI_INITIALIZE_FLAG_USES_SKELETON);
	//NUI_SKELETON_FRAME ourframe;
	//while (1)
	//{
	//	HRESULT res = NuiSkeletonGetNextFrame(0, &ourframe);
	//	for (int i = 0; i < 6; i++)
	//	{
	//		if (ourframe.SkeletonData[i].eTrackingState == NUI_SKELETON_TRACKED)
	//			cout << "Right Hand: ";
	//		cout << ourframe.SkeletonData[i].SkeletonPositions[NUI_SKELETON_POSITION_HAND_RIGHT].y << endl;
	//	}
	//	system("cls");
	//}
	//NuiShutdown();


	return 0;
}