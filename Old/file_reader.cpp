#include <iostream>
#include <string>
#include <fstream>
#include <sstream>
#include <vector>
#include <string>

using namespace std;
class ProcessData {
public:
	string ReadData (string filename);
	vector <string> SplitByDel (string data, string delimiter);
};
string ProcessData::ReadData(string filename) {
	string data = "";
	string lineData;
	ifstream ReadFile(filename);
	if (!ReadFile) {
		cout << "read error";
	}
	while (getline(ReadFile, lineData)) {
		data += lineData + "\n";
	}
	return data;
}

vector <string> ProcessData::SplitByDel(string data, string delimiter) {
	vector <string> vector_data;
	int pos = 0;
	string token;
	while ((pos = data.find(delimiter)) != string::npos) {
		token = data.substr(0, pos);
		vector_data.push_back(token);
		data.erase(0, pos + delimiter.length());
	}
	vector_data.push_back(data);
	
	return vector_data;
}


int main() {
	
	ProcessData process;
	string data = process.ReadData("sample_text.txt");
	vector <string> vector_data = process.SplitByDel(data, "///");
	for (auto i = vector_data.begin(); i != vector_data.end(); ++i)
		std::cout << *i << ' ';
	
	
}

