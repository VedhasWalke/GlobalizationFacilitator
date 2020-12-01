#include <iostream>
#include <string>
#include <fstream>
#include <sstream>
#include <vector>

/*
Just what we have rn, I'll applicable version later
*/
void print(std::vector<std::string> const& input)
{
	for (int i = 0; i < input.size(); i++) {
		std::cout << input.at(i) << ' ';
	}
}
int main() {
	using namespace std;
	string array[10];
	ifstream inFile("sample_text.txt");
	string line;
	int loop = 0;
	if (inFile.is_open())
	{ 
		while (!inFile.eof())
		{
			getline(inFile, line);
			array[loop] = line;
			cout << array[loop] << endl;
			loop++;
		}
		inFile.close();
	}
	else
	{
		cout << "Can't open file";

	}
	return 0;
		
}