#pragma once


typedef struct
{
	void* hFileMap;
	void* pData;
	char MapName[256];
	size_t Size;
} SharedMemory;


bool CreateMemoryMap(SharedMemory* shm);
bool FreeMemoryMap(SharedMemory* shm);
int connexion();
void test();