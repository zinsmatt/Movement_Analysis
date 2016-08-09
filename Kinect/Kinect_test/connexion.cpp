#include <windows.h>
#define _CRT_SECURE_NO_WARNINGS

#include <cstring>
#include <cstdbool>
#include <iostream>
#include <chrono>
#include <ctime>
#include "connexion.h"
#include <vector>

using namespace std::chrono;


bool CreateMemoryMap(SharedMemory* shm)
{
	if ((shm->hFileMap = CreateFileMapping(INVALID_HANDLE_VALUE, NULL, PAGE_READWRITE, 0, shm->Size, shm->MapName)) == NULL)
	{
		return false;
	}

	if ((shm->pData = MapViewOfFile(shm->hFileMap, FILE_MAP_ALL_ACCESS, 0, 0, shm->Size)) == NULL)
	{
		CloseHandle(shm->hFileMap);
		return false;
	}
	return true;
}

bool FreeMemoryMap(SharedMemory* shm)
{
	if (shm && shm->hFileMap)
	{
		if (shm->pData)
		{
			UnmapViewOfFile(shm->pData);
		}

		if (shm->hFileMap)
		{
			CloseHandle(shm->hFileMap);
		}
		return true;
	}
	return false;
}

int connexion()
{
	SharedMemory shm = { 0 };
	shm.Size = 512;
	sprintf(shm.MapName, "Local\\Test");

	if (CreateMemoryMap(&shm))
	{
		char* ptr = (char*)shm.pData;
		memset(ptr, 0, shm.Size);

		while (ptr && (*ptr == 0))
		{
			//Sleep(100);
		}
		// msg recu


		long long ms = duration_cast<std::chrono::milliseconds>(system_clock::now().time_since_epoch()).count();
		std::cout << "ms = " << ms << std::endl;


		long long s = duration_cast<std::chrono::milliseconds>(system_clock::now().time_since_epoch()).count();
		std::cout << "ss = " << s << std::endl;

		int size = (int)*ptr;
		ptr += sizeof(char);

		int i = 0;
		for (; i < size; ++i)
		{
			std::cout << ptr[i];
		}
		std::cout << std::endl;
		FreeMemoryMap(&shm);
	}
	return 0;
}

void test() {

	std::vector<int> v1;

	while (1)
	{
		long long t1 = duration_cast<std::chrono::milliseconds>(system_clock::now().time_since_epoch()).count();
		v1.push_back(32);
		v1.push_back(33);
		v1.push_back(32);
		v1.push_back(33); v1.push_back(32);
		v1.push_back(33);
		Sleep(1);

		long long t2 = duration_cast<std::chrono::milliseconds>(system_clock::now().time_since_epoch()).count();

		std::cout << t1 << std::endl;
		std::cout << t2 << std::endl << std::endl;

	}
}