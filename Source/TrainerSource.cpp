/*
Main Algorithm Prototype

Date Updated: 12/30/20

Description:
	Machine learning training algorithm based on Naive Bayes Framework.
	Uses two data sets of customer reviews of a business: positive reviews
	and negative reviews. Outputs file containing computed optimal features
	in special format as detailed in "ParametersFormat.txt" file in "Help"
	directory.

Non-primitive Data Types:
	WordSet: a struct housing multiple variables key to analyzing a set of reviews.
		counts: vector storing number of instances of each word in all reviews of the wordset.
		pcounts: vector storing number of instances of each word in all positive reviews of the wordset.
		ncounts: vector storing number of instances of each word in all negative reviews of the wordset.
		numberOfmembers: number of words contained in a wordset, equivalent to size of counts vector.

Functions:
	Union: combines two wordsets(positive and negative in this case) into one.
	Compress: converts raw words into a word set.
	OutputFile: outputs parameters found in a text document

*/

#include <iostream>
#include <vector>
#include <fstream>
#include <numeric>
#include <string>
#include <algorithm>
#include <ctime>
using namespace std;



struct WordSet {
	vector<string> words;
	vector<int> counts;
	vector<int> pcounts;
	vector<int> ncounts;
	int numberOfmembers = 0;

};



// Prototypes
WordSet ProcessDocument(string filename);
string Preformat(string raw_word);
WordSet Union(WordSet Pos, WordSet Neg);
WordSet Compress(vector<string> raw_words);
void OutputFile(WordSet All, vector<double> OtherData);






string getDate() {
	time_t rawtime;
	struct tm timeinfo;
	char buffer[80];



	time(&rawtime);
	localtime_s(&timeinfo, &rawtime);

	strftime(buffer, sizeof(buffer), "%m-%d-%Y %H:%M:%S", &timeinfo);
	string str(buffer);
	return str;
}

WordSet ProcessDocument(string filename) {
	
	ifstream inputFile;
	inputFile.open(filename);

	vector<string> raw_words;
	string word;
	while (inputFile) {
		inputFile >> word;
		raw_words.push_back(Preformat(word));
	}

	return Compress(raw_words);

} 

string Preformat(string raw_word) {
	for (int i = 0; i < raw_word.size(); i++) {
		if (raw_word[i] == '\"')
			raw_word.erase(raw_word.begin()+i);
	}
	return raw_word;
}

WordSet Union(WordSet Pos, WordSet Neg) {
	int max_elem;
	if (Pos.numberOfmembers > Neg.numberOfmembers)
		max_elem = Neg.numberOfmembers;
	else
		max_elem = Pos.numberOfmembers;
	// max_elem is max element of looping, not string count(looping cannot exceed size of any array)

	vector<string> words(Pos.numberOfmembers + Neg.numberOfmembers);
	vector<int> counts(Pos.numberOfmembers + Neg.numberOfmembers);
	vector<int> pcounts(Pos.numberOfmembers + Neg.numberOfmembers);
	vector<int> ncounts(Pos.numberOfmembers + Neg.numberOfmembers);
	int i = 0; // pos iterator
	int j = 0; // neg iterator
	int m = 0; // words iterator
	for (int k = 0; k < max_elem; k++) {

		if (Pos.words[i].compare(Neg.words[j]) < 0) {

			words[m] = Pos.words[i];
			counts[m] = Pos.counts[i];
			pcounts[m] = Pos.counts[i];
			i++;
			m++;

		}
		else if (Pos.words[i].compare(Neg.words[j]) > 0) {
			words[m] = Neg.words[j];
			counts[m] = Neg.counts[j];
			ncounts[m] = Neg.counts[j];
			j++;
			m++;
		}
		else {
			words[m] = Pos.words[i];
			counts[m] = Pos.counts[i] + Neg.counts[j];
			ncounts[m] = Neg.counts[j];
			pcounts[m] = Pos.counts[i];
			i++;
			j++;
			m++;
		}
	}



	for (; m < Pos.numberOfmembers - 1; m++) {
		words[m] = Pos.words[i];
		counts[m] = Pos.counts[i];
		pcounts[m] = Pos.counts[i];
		i++;
	}

	for (; m < Neg.numberOfmembers - 1; m++) {
		words[m] = Neg.words[j];
		counts[m] = Neg.counts[j];
		ncounts[m] = Neg.counts[j];
		j++;
	}

	
	// erasing empty elements of words, counts, pcounts, and ncounts vectors.
	words.erase(words.begin() + m, words.end());
	counts.erase(counts.begin() + m, counts.end());
	pcounts.erase(pcounts.begin() + m, pcounts.end());
	ncounts.erase(ncounts.begin() + m, ncounts.end());


	WordSet C;
	C.counts = counts;
	C.words = words;
	C.ncounts = ncounts;
	C.pcounts = pcounts;
	C.numberOfmembers = words.size();

	return C;
}

WordSet Compress(vector<string> raw_words) {
	sort(raw_words.begin(), raw_words.end());

	vector<int> counts(raw_words.size(), 1);
	vector<string> words(raw_words.size(), "");


	words[0] = raw_words[0];

	int j = 0; // counts and words iterator
	for (int i = 1; i < raw_words.size(); i++) {
		if (raw_words[i] == raw_words[i - 1]) {
			counts[j]++;
		}
		else {
			j++;
			words[j] = raw_words[i];
		}


	}

	counts.erase(counts.begin() + j + 1, counts.end());
	words.erase(words.begin() + j + 1, words.end());

	if (words[0] == "") { // can't have first element as nothing
		words.erase(words.begin());
		counts.erase(counts.begin());
	}


	WordSet A;
	A.counts = counts;
	A.words = words;
	A.numberOfmembers = A.words.size();

	return A;
}

void OutputFile(WordSet All, vector<double> OtherData) {

	ofstream outf;



	// First Parameters File: word counts
	outf.open("ModelParameters\\Param1.txt");
                     
	// Preliminary Information
	outf << "Parameters for Naive Bayes\n";
	outf << "(Word Counts)\n";
	outf << "Last Modified: " << getDate() << "\n";
	outf << "#" << "\n"; // Data Starts Here

	for (int i = 0; i < All.numberOfmembers; i++) {
		outf << All.words[i] << " " << All.counts[i] << " " << All.pcounts[i] << " " << All.ncounts[i] << "\n";
	}
	outf << "#";

	outf.close();
	 



	// Second Parameter File: Class Probabilities and Sums
	outf.open("ModelParameters\\Param2.txt");
	outf << "Parameters for Naive Bayes\n";
	outf << "(Class Probability and Sums Data)\n";
	outf << "Last Modified: " << getDate() << "\n";
	outf << "#" << "\n"; // Data Starts Here

	
		outf << OtherData[0] << "\n" << OtherData[1] << "\n" << OtherData[2] << "\n" << OtherData[3] << "\n" << OtherData[4] << "\n" << OtherData[5];
		outf << "\n";
	
	outf << "#";
	outf.close();

}



int main()
{ 

	 
	 
	
	//"C:\\Users\\yoges\\OneDrive\\Documents\\GFacil\\AlgorithmFiles\\TRAINER\\PosTrainingSet\\PosTrainingSet.txt";
	WordSet Pos = ProcessDocument("PosTrainingSet\\PosTrainingSet.txt");
	
	//"C:\\Users\\yoges\\OneDrive\\Documents\\GFacil\\AlgorithmFiles\\TRAINER\\NegTrainingSet\\NegTrainingSet.txt";
	WordSet Neg = ProcessDocument("NegTrainingSet\\NegTrainingSet.txt");

	WordSet All = Union(Pos, Neg);


	 
	int N = All.numberOfmembers;

	int sum = accumulate(All.counts.begin(), All.counts.end(), 0);
	int psum = accumulate(All.pcounts.begin(), All.pcounts.end(), 0);
	int nsum = accumulate(All.ncounts.begin(), All.ncounts.end(), 0);

	// Laplace Smoothing Here



	// OtherData: PcPos  PcNeg  sum  psum  nsum numberOfmembers
	vector<double> OtherData(6);

	OtherData[0] = Neg.numberOfmembers / (double)All.numberOfmembers;
	OtherData[1] = Pos.numberOfmembers / (double)All.numberOfmembers;
	OtherData[2] = sum;
	OtherData[3] = psum;
	OtherData[4] = nsum;
	OtherData[5] = All.numberOfmembers;

	// Training Completed

	OutputFile(All, OtherData);



}

