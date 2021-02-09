

#include <iostream>
#include <vector>
#include <string>
#include <fstream>
using namespace std;

struct WordSet {
	vector<string> words;
	vector<int> counts;
	vector<int> pcounts;
	vector<int> ncounts;
	int numberOfmembers = 0;

};

struct Review {
	vector<string> words;
	int sentiment;
	string first_name;
	string last_name;
	int date[3];
};

// Global Variables
WordSet set;


// Function Prototypes
WordSet DocToSet(vector<double>& OtherData); // conversion from document to wordset data structure
int IndexOf(string word, double index, int power); // return index of a word in the set



WordSet DocToSet(vector<double>& OtherData) {
	ifstream features;

	features.open("..\\TRAINER\\ModelParameters\\Param2.txt");
	char c = '1';
	while (c != '#') {
		features.get(c);
	}
	features.get(); // ignore newline
	double param;
	for (int i = 0; i < 6; i++) {
		features >> param;
		OtherData.push_back(param);
	}


	features.close();
	features.open("..\\TRAINER\\ModelParameters\\Param1.txt");

	c = '1';
	while (c != '#') {
		features.get(c);
	}
	features.get(); // ignore newline

	
	vector<string> words((int)OtherData[5]);
	vector<int> counts((int)OtherData[5]), pcounts((int)OtherData[5]), ncounts((int)OtherData[5]);

	int i = 0;
	while (i < words.size()) {
		features >> words[i];
		features >> counts[i];
		features >> pcounts[i];
		features >> ncounts[i];
		i++;
	}

	WordSet C;
	C.counts = counts;
	C.words = words;
	C.ncounts = ncounts;
	C.pcounts = pcounts;
	C.numberOfmembers = OtherData[5];

	return C;

}

bool IsValid(int index) {
	if (index < set.words.size() && index >= 0)
		return true;
	else
		return false;
}

int IndexOf(string word, double index, int power) {
	
	if (set.numberOfmembers*2 / power <= 3) {
		if (IsValid((int)index - 5) && set.words[(int)index - 5] == word)
			return (int)index - 5;
		if (IsValid((int)index - 4) && set.words[(int)index - 4] == word)
			return (int)index - 4;
		if (IsValid((int)index - 3) && set.words[(int)index - 3] == word)
			return (int)index - 3;
		if (IsValid((int)index - 2) && set.words[(int)index - 2] == word)
			return (int)index - 2;
		if (IsValid((int)index - 1) && set.words[(int)index - 1] == word)
			return (int)index - 1;
		if (IsValid((int)index + 1) && set.words[(int)index + 1] == word)
			return (int)index + 1;
		if (IsValid((int)index + 2) && set.words[(int)index + 2] == word)
			return (int)index + 2;
		if (IsValid((int)index + 3) && set.words[(int)index + 3] == word)
			return (int)index + 3;
		if (IsValid((int)index + 4) && set.words[(int)index + 4] == word)
			return (int)index + 4;
		if (IsValid((int)index + 5) && set.words[(int)index + 5] == word)
			return (int)index + 5;

		return set.numberOfmembers;
	}

	if (set.words[(int)index] == word)
		return (int)index;
	else if (set.words[(int)index].compare(word) < 0) {
		return IndexOf(word, index + (double)set.numberOfmembers / power, power*2);
	}
	else
		return IndexOf(word, index - (double)set.numberOfmembers / power, power*2);

	


}





int main()
{
	vector<double> OtherData;
	set = DocToSet(OtherData);
	ifstream inputFile;
	//"Metadata\\IO_Num.txt"
    // "C:\\Users\\yoges\\OneDrive\\Documents\\GFacil\\AlgorithmFiles\\MAIN\\Metadata\\IO_Num.txt"
	inputFile.open("C:\\Users\\yoges\\OneDrive\\Documents\\GFacil\\AlgorithmFiles\\MAIN\\Metadata\\IO_Num.txt");
	string FileNum;
	inputFile >> FileNum;
	inputFile.close();
	// "C:\\Users\\yoges\\OneDrive\\Documents\\GFacil\\Input\\I" + FileNum + ".txt"
	//"..\\..\\Input\\" + FileNum + ".txt"
	inputFile.open("C:\\Users\\yoges\\OneDrive\\Documents\\GFacil\\Input\\I" + FileNum + ".txt");
	
	//cout << " and there";
	Review review;

	string word;
	while (inputFile) {
		inputFile >> word;
		review.words.push_back(word);
	}


	long long pcountsProduct = 1; // product of word counts given positive class
	long long ncountsProduct = 1; // product of word counts given negative class
	int pcountsProductTens = 0;
	int ncountsProductTens = 0;
	for (int i = 0; i < review.words.size(); i++) {
		int index = IndexOf(review.words[i], set.numberOfmembers/2, 4);
		
		
		if (index != set.words.size()) {
			pcountsProduct *= (set.pcounts[index]+(long long)1); // Add 1 for Laplace Smoothing
			ncountsProduct *= (set.ncounts[index]+(long long)1); // Add 1 for Laplace Smoothing
		}

		if (pcountsProduct > (1000000000000000000)) {
			pcountsProduct /= (1000000000000000000);
			pcountsProductTens++;
		}
		if (ncountsProduct > (1000000000000000000)) {
			ncountsProduct /= (1000000000000000000);
			ncountsProductTens++;
		}
	}
	
	ofstream outputFile;
	outputFile.open("..\\..\\Output\\O" + FileNum + ".txt");


	if (pcountsProductTens > ncountsProductTens)
		outputFile << "Positive";
	else if (ncountsProductTens > pcountsProductTens)
		outputFile << "Negative";
	else if (pcountsProduct > ncountsProduct)
		outputFile << "Positive";
	else if (ncountsProduct > pcountsProduct)
		outputFile << "Negative";
	else
		outputFile << "Equal";

	
}
