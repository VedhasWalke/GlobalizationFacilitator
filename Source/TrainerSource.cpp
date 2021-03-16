/*
Trainer System

Date Updated: 3/14/21

Description:
	Machine learning training algorithm based on Naive Bayes Framework.
	Uses two main data sets of customer reviews of a business: positive reviews
	and negative reviews. Furthermore, uses two auxilary datasets of highly specific,
	hand-picked data on the loyalty of a consumer based on review. Outputs file
	containing computed optimal features in special format as detailed in
	"ParametersFormat.txt" file in "Help" directory.

Non-primitive Data Types:
	vector<word>: a struct housing multiple variables key to analyzing a set of reviews.
		counts: vector storing number of instances of each word in all reviews of the vector<word>.
		pcounts: vector storing number of instances of each word in all positive reviews of the vector<word>.
		ncounts: vector storing number of instances of each word in all negative reviews of the vector<word>.
		numberOfmembers: number of words contained in a vector<word>, equivalent to size of counts vector.

Functions:
	Union: combines two vector<word>s(positive and negative in this case) into one.
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
#include <iterator>
using namespace std;


struct counts {
	int p; // positive counts
	int n; // negative counts
	int o; // novel counts
	int l; // loyal counts
};

struct word {
	string text;
	counts count;
	int value;
};



// Global Variables
ofstream Log;
int SetType; // 0 -> positive, 1 -> negative, 2 -> novel, 3 -> loyal
int punctuationCounts[4][3];
int OtherData[4][4] = { { 0,0,0,0 }, { 0,0,0,0 }, { 0,0,0,0 }, {0,0,0,0} };
//         0              1              2             3               
//  uniqueWordCountP 
//   rawWordCountP  rawWordCountN  rawWordCountO  rawWordCountL   
//   numPosReviews  numNegReviews  numNovReviews  numLoyReviews  
//      ngramP         ngramN           ngramO       ngramL



// Constants
const string AbsPath = "C:\\Users\\750010316\\Documents\\GFacil\\GlobalizationFacilitator\\AlgorithmFiles\\TRAINER\\";
const string LogFileName = "Log.txt";
const string Param1FileName = "ModelParameters\\Param1.txt";
const string Param2FileName = "ModelParameters\\Param2.txt";
const string posDataFileName = "TrainingSets\\PosTrainingSet\\PosTrainingSet.txt";
const string negDataFileName = "TrainingSets\\NegTrainingSet\\NegTrainingSet.txt";
const string novDataFileName = "TrainingSets\\NovTrainingSet\\NovTrainingSet.txt";
const string loyDataFileName = "TrainingSets\\LoyTrainingSet\\LoyTrainingSet.txt";
const string metadataFolderName = "Metadata\\";

// Metadata
string delimiter;
string taboo_chars;
vector<string> stop_words;
vector<string> negation_words;


// Prototypes
vector<word> ProcessDocument(string filename, int ngram);
string Preprocess(string raw_word);
vector<word> Union(vector<vector<word>> All);
vector<word> Compress(vector<string> raw_words);
vector<word> Trim(vector<vector<word>> All);
int Evaluate(counts c);
void OutputFile(vector<word>::iterator set, int n);





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

vector<word> ProcessDocument(string filename, int ngram) {

	ifstream inputFile;
	inputFile.open(filename);

	// CHECK
	if (inputFile) {
		Log.open(AbsPath + LogFileName, ostream::out | ostream::app);
		Log << getDate() << " | " << filename.substr(filename.find_last_of('\\') + 1) << " opened successfully " << endl;
		Log.close();
	}
	else {
		Log.open(AbsPath + LogFileName, ostream::out | ostream::app);
		Log << getDate() << " | ERROR: Filename invalid |" << filename.substr(filename.find_last_of('\\') + 1) << " did not opened successfully" << endl;
		Log.close();
	}


	vector<string> raw_words, refined_phrases;
	string phrase, temp;
	vector<vector<word>> All(ngram);

	while (inputFile) {
		inputFile >> temp;
		raw_words.push_back(temp);
	}


	// adding some OtherData
	OtherData[1][SetType] = raw_words.size();
	OtherData[3][SetType] = ngram;
	for (int i = 0; i < raw_words.size(); i++) {
		if (raw_words[i] == delimiter)
			OtherData[2][SetType]++;
	}



	for (int n = 1; n <= ngram; n++) {
		int i = 0;
		refined_phrases.clear();

		while (i < raw_words.size() - n) {
			phrase = "";
			for (int j = 0; j < n; j++) {
				phrase += raw_words[i + j] + " ";
			}
			phrase.erase(phrase.end() - 1);


			if (phrase.find(delimiter) != string::npos) {
				i += n;
				continue;
			}

			refined_phrases.push_back(Preprocess(phrase));
			i++;
		}
		All[n - 1] = Compress(refined_phrases);
	}


	return Trim(All);


}

string Preprocess(string raw_word) {

	//deleting taboo characters as defined by "taboo_chars" array
	size_t t = raw_word.find_first_of(taboo_chars);
	while (t != string::npos) {
		raw_word.erase(t);
		t = raw_word.find_first_of(taboo_chars);
	}

	

	// deleting stopwords
	raw_word.insert(raw_word.begin(), ' ');
	raw_word.insert(raw_word.end(), ' ');

	for (int i = 0; i < stop_words.size(); i++) {
		t = raw_word.find(" " + stop_words[i] + " ");
		if (t != string::npos)
			raw_word.erase(t+1, t + stop_words[i].size());
	}
	raw_word.erase(raw_word.begin());
	raw_word.erase(raw_word.end()-1);


	// checking for punctuation
	for (int i = 0; i < raw_word.size(); i++) {

		if (raw_word[i] == '.') {
			punctuationCounts[SetType][0]++;
			raw_word.erase(i);
		}
		else if (raw_word[i] == '!') {
			punctuationCounts[SetType][1]++;
			raw_word.erase(i);
		}
		else if (raw_word[i] == '?') {
			punctuationCounts[SetType][2]++;
			raw_word.erase(i);
		}
		else {
			i++;
		}
		i--; // if punctuation char was deleted
	}

	for (int i = 0; i < raw_word.size(); i++) {
		raw_word[i] = tolower(raw_word[i]);
	}

	return raw_word;
}


vector<word> Union(vector<vector<word>> All) { // lazily coded, kinda slow
	vector<word> c = All[0];

	// combining all vectors into one
	for (int i = 1; i < All.size(); i++) {
		c.insert(c.end(), All[i].begin(), All[i].end());
	}

	// sorting
	sort(c.begin(), c.end(), [](word a, word b) {return a.text < b.text; });

	int num = 0;
	vector<word> cset;
	// combining adjacent words into one
	for (int i = 0; i < c.size() - 1; i++) {

		if (c[i].text == c[i + 1].text) {
			num++;
		}
		else {
			int p = 0;
			int n = 0;
			int o = 0;
			int l = 0;

			for (int j = i; j >= i - num; j--) {
				p += c[j].count.p;
				n += c[j].count.n;
				o += c[j].count.o;
				l += c[j].count.l;
			}

			cset.push_back(word{ c[i].text,{p,n,o,l}, Evaluate({p,n,o,l}) });
		}
	}


	return cset;
}


vector<word> Compress(vector<string> raw_words) { // CHECK
	sort(raw_words.begin(), raw_words.end());

	int count = 1;
	string text = "";
	vector<word> set;

	text = raw_words[0];
	for (int i = 1; i < raw_words.size(); i++) {
		if (raw_words[i] == text) {
			count++;
		}
		else {

			counts c = { 0,0,0,0 };
			if (SetType == 0)
				c.p = count;
			else if (SetType == 1)
				c.n = count;
			else if (SetType == 2)
				c.o = count;
			else if (SetType == 3)
				c.l = count;

			set.push_back(word{ text, c, Evaluate(c) }); // correct struct declaration?
			count = 1;
			text = raw_words[i];
		}
	}



	if (set[0].text == "") {
		set.erase(set.begin());
	}


	return set;
}

int Evaluate(counts c) {

	return c.p + c.n + c.o + c.l;

}

// temporary trimming --> lopping off bottom half
vector<word> Trim(vector<vector<word>> All) {



	for (int i = 0; i < All.size(); i++) {

		for (vector<word>::iterator j = All[i].begin(); j < All[i].end(); j++) {
			Evaluate((*j).count);
		}
		sort(All[i].begin(), All[i].end(), [](word a, word b) {return a.value > b.value; }); // sorting in correct order?

		All[i].erase(All[i].begin() + All[i].size() / 2, All[i].end()); // how much to trim?? (rn just lopping off bottom half values)
	}



	return Union(All);



}



void OutputFile(vector<word>::iterator set, int n) {

	ofstream outf;



	// First Parameters File: Word Counts
	outf.open(AbsPath + Param1FileName);

	// Preliminary Information
	outf << "Parameters for Naive Bayes\n";
	outf << "(Word Counts)\n";
	outf << "<text> [p] [n] [o] [l]\n";
	outf << "Last Modified: " << getDate() << "\n";
	outf << "#" << "\n"; // Data Starts Here

	for (int i = 0; i < n; i++) {
		outf << (*set).text << " " << (*set).count.p << " " << (*set).count.n << " " << (*set).count.o << " " << (*set).count.l << endl;
		set++;
	}

	outf << "#";

	outf.close();




	// Second Parameter File: Qualities of Word Counts
	outf.open(AbsPath + Param2FileName);
	outf << "Parameters for Naive Bayes\n";
	outf << "(Class Probability and Sums Data)\n";
	outf << "Last Modified: " << getDate() << "\n";
	outf << "#" << "\n"; // Data Starts Here

	for (int i = 0; i < 4; i++) {
		for (int j = 0; j < 4; j++) {
			outf << OtherData[i][j] << " ";
		}
		outf << "\n";
	}

	outf << "\n\n";

	for (int i = 0; i < 4; i++) {
		for (int j = 0; j < 3; j++) {
			outf << punctuationCounts[i][j] << " ";
		}
		outf << "\n";
	}

	outf << "#";
	outf.close();

	Log.open(AbsPath + LogFileName, ostream::out | ostream::app);
	Log << getDate() << " | Training Completed\n\n";


	// Third Parameter File: 

}





















int main() {

	
	// Setup

	Log.open(AbsPath + LogFileName, ostream::out | ostream::app);

	for (int i = 0; i < 4; i++) {
		for (int j = 0; j < 3; j++) {
			punctuationCounts[i][j] = 0;
		}
	}

	ifstream inFile;
	string temp;
	vector<string> taboo_chars2;
	char temp2;
	inFile.open(AbsPath + metadataFolderName + "Delimiter.txt");
	inFile >> delimiter;
	inFile.close();
	inFile.open(AbsPath + metadataFolderName + "StopWordList.txt");
	while (inFile) {
		inFile >> temp;
		stop_words.push_back(temp);
	}
	inFile.open(AbsPath + metadataFolderName + "NegationWords.txt");
	while (inFile) {
		inFile >> temp;
		negation_words.push_back(temp);
	}
	inFile.open(AbsPath + metadataFolderName + "TabooChars.txt");
	while (inFile) {
		inFile >> temp;
		taboo_chars2.push_back(temp);
	}
	taboo_chars = "";
	for (int i = 0; i < taboo_chars2.size(); i++) {
		taboo_chars = taboo_chars + taboo_chars2[i];
	}

	// Positive/Negative Training
	SetType = 0;
	vector<word> Pos = ProcessDocument(AbsPath + posDataFileName, 2);
	SetType = 1;
	vector<word> Neg = ProcessDocument(AbsPath + negDataFileName, 2);
	SetType = 2;
	vector<word> Nov = ProcessDocument(AbsPath + novDataFileName, 3);
	SetType = 3;
	vector<word> Loy = ProcessDocument(AbsPath + loyDataFileName, 3);
	vector<word> All = Union({ Pos, Neg, Nov, Loy });


	// OtherData: PcPos  PcNeg  sum  psum  nsum numberOfmembers
	vector<double> OtherData(6);





	// OtherData: PcPos  PcNeg  sum  psum  nsum numberOfmembers

	OutputFile(All.begin(), All.size());
}

